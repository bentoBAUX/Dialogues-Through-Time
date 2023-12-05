using System;
using System.Collections;
using System.Text;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.Serialization;
using UnityEngine.UI;

using UnityEngine.Networking;
using SimpleJSON;
using UnityEngine.SceneManagement;

public class ChatManager : MonoBehaviour
{

  public AnimCtrl currentCharacter;

    
  public GameObject chatPanel;
    
  public GameObject playerTextBubble;

  public GameObject AITextBubble;

    
  public TMP_InputField chatBox;

  [SerializeField] private bool playerSent = false;
    
  [SerializeField]
  private List<Message> messageList = new List<Message>();

  private string uniqueId = "";
  private bool processing = false;



  void Start()
  {
    //get id 
    LoadUniqueId();
    FetchAndSetChatHistory();
    StartCoroutine(StartPostChatStreamAfterDelay("I was gone for a while but i am back now. greetings.", false));
		currentCharacter.Idle();
		
    /*example of setting triggers
    currentCharacter.Talk();
    currentCharacter.Idle();
    */
	}



  void Update()
  {
      //send text
      if (chatBox.text != "")
      {
          if (Input.GetKeyDown(KeyCode.Return) && !string.IsNullOrEmpty(uniqueId))
          {
              StartCoroutine(PostChatStream(chatBox.text));
          }
      }
      else
      {
          if (!chatBox.isFocused && Input.GetKeyDown(KeyCode.Return))
          {
              chatBox.ActivateInputField();
          }
      }

    //remove the unique id and restart
    if (Input.GetKeyDown(KeyCode.F4))
    {
      removeSavedUniqueId();
      ClearChatHistory();
      SceneManager.LoadScene("Entity");
    }
    if (Input.GetKeyDown(KeyCode.F5))
    {
      removeSavedUniqueId();
      SceneManager.LoadScene("Intro");
    }

    //end conversation
    if (Input.GetKeyDown(KeyCode.F10))
		{
      LeaveChat();
		}
  }

  public void LeaveChat()
  {
		StartCoroutine(PostChatStream("", false, true));
	}

	#region /// get ID
	void LoadUniqueId()
  {
    uniqueId = PlayerPrefs.GetString("UniqueID", "");

    if (string.IsNullOrEmpty(uniqueId))
    {
      StartCoroutine(GetUniqueIdFromServer());
    }
    else
    {
      Debug.Log("Loaded saved Unique ID: " + uniqueId);
    }
  }

  IEnumerator GetUniqueIdFromServer()
  {
    using (UnityWebRequest webRequest = UnityWebRequest.Get(Utilities.serverUrl + "/get_unique_id"))
    {
      // Request and wait for the desired page.
      yield return webRequest.SendWebRequest();

      if (webRequest.isNetworkError || webRequest.isHttpError)
      {
        Debug.Log(": Error: " + webRequest.error);
      }
      else
      {
        var jsonResponse = webRequest.downloadHandler.text;
        var uniqueIdResponse = JsonUtility.FromJson<UniqueIdResponse>(jsonResponse);
        uniqueId = uniqueIdResponse.id;
        Debug.Log("Received unique ID from server: " + uniqueId);
        SaveUniqueId();
      }
    }
  }

  [Serializable]
  private class UniqueIdResponse
  {
    public string id;
  }
  void SaveUniqueId()
  {
    // Save the unique ID in PlayerPrefs for persistence
    PlayerPrefs.SetString("UniqueID", uniqueId);
    PlayerPrefs.Save();
  }

  // Method to retrieve the unique ID
  public string GetSavedUniqueId()
  {
    return PlayerPrefs.GetString("UniqueID", "");
  }
  public void removeSavedUniqueId()
	{
    PlayerPrefs.DeleteKey("UniqueID");
	}
  #endregion

  #region ///send chat to api
  private string GetChatUrl()
  {
    return $"{Utilities.serverUrl}/chat";
  }

  IEnumerator StartPostChatStreamAfterDelay(string message, bool someBoolean)
  {
    yield return new WaitForSeconds(2); // Wait for 3 seconds
    StartCoroutine(PostChatStream(message, someBoolean));
  }

  IEnumerator PostChatStream(string message,bool player_bubble = true,bool end_conversation = false)
  {
    if (processing)
		{
      Debug.LogError("Message from ai already processing");
      yield break;
		}

    //init
    processing = true;
    chatBox.text = "";
    if (player_bubble) SendMessageToChat(message, Message.MessageType.playerMessage);

    // URL encode the message and unique ID
    string encodedMessage = UnityWebRequest.EscapeURL(message);
    string encodedUniqueId = UnityWebRequest.EscapeURL(GetSavedUniqueId());

    // Construct the GET URL with query parameters
    string url = GetChatUrl() + $"?user_msg={encodedMessage}&unique_id={encodedUniqueId}&end_conversation={end_conversation}";

    // Create a POST UnityWebRequest
    using (UnityWebRequest request = UnityWebRequest.Get(url))
    {
      request.downloadHandler = new DownloadHandlerBuffer();
      request.SendWebRequest();
      bool streamEnded = false;
      string lastResponse = "";
      bool talking = false;

      //create message box
      Message messageBox = SendMessageToChat("", Message.MessageType.AIMessage);

			//timeout
			float timeSinceLastUpdate = 0f;
			float timeoutDuration = 30f; // 30 seconds timeout duration

			//start adding text to the message box
			while (!streamEnded)//(!streamEnded)
      {

        if (request.result == UnityWebRequest.Result.ConnectionError ||
            request.result == UnityWebRequest.Result.ProtocolError)
        {
          processing = false;
          Debug.LogError(request.error);
          Debug.Log("ending request");
          yield break;
        }


        //received the response
        if (request.downloadHandler != null && request.downloadHandler.data != null)
        {
          string response = request.downloadHandler.text;
          if (response != lastResponse)
          {
						// Reset the timeout tracker on receiving new data
						timeSinceLastUpdate = 0f;
						
            //set talking animation
            if (!talking)
            {
							currentCharacter.Talk();
              talking = true;
						}

            //handle data
            string newData = response.Substring(lastResponse.Length);
            if (!string.IsNullOrEmpty(newData))
            {
              //we get the json response from the server
              var chatJson = JSON.Parse(newData);
              if (chatJson.HasKey("ai_speaking"))
              {
                string aiResponse = chatJson["ai_speaking"];
                //if server sending second bubble
                if (aiResponse.Length < messageBox.text.Length ) messageBox = SendMessageToChat("", Message.MessageType.AIMessage);
                messageBox.text = aiResponse;
                messageBox.textObject.text = aiResponse;
              }

              Debug.Log(chatJson);

              //end streaming if json says it
              streamEnded = chatJson.HasKey("streaming");

              ///Things that happen after finishes talking

              //end conversation and change scene
              if (streamEnded)
              {
                if (chatJson["end_reason"] == "end_conversation")
                {
                  if (Utilities.sceneMap.TryGetValue(chatJson["current_scene"], out string value))
                  {
                    StartCoroutine(ChangeSceneWithDelay(value));
                  }
                  else
                  {
                    Debug.LogError("Scene from server doesnt exist!" + chatJson["current_scene"]);
                  }
                }

                //set chat history
                if (chatJson.HasKey("render_chat_history") && chatJson["end_reason"] != "end_conversation") SetChatHistory(chatJson["render_chat_history"].AsArray);
              }
            }

            lastResponse = response;
          }
        }

				// Check for timeout
				timeSinceLastUpdate += Time.deltaTime;
				if (timeSinceLastUpdate >= timeoutDuration)
				{
					processing = false;
					Debug.LogError("Timeout Error: No response received for " + timeoutDuration + " seconds.");
					yield break;
				}

				// Wait before checking for more data
				yield return new WaitForSeconds(0.2f);
      }

			currentCharacter.Idle();
			processing = false;
      Debug.Log("end");
    }
  }

  IEnumerator ChangeSceneWithDelay(string sceneName)
  {
    yield return new WaitForSeconds(2); // Wait for 4 seconds
    SceneManager.LoadScene(sceneName);
  }


  public void FetchAndSetChatHistory()
  {
    StartCoroutine(GetChatHistoryCoroutine());
  }

  private IEnumerator GetChatHistoryCoroutine()
  {
    string url = $"{Utilities.serverUrl}/chat_history/{GetSavedUniqueId()}";
    using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
    {
      // Request and wait for the desired page.
      yield return webRequest.SendWebRequest();

      if (webRequest.result == UnityWebRequest.Result.ConnectionError ||
          webRequest.result == UnityWebRequest.Result.ProtocolError)
      {
        Debug.LogError(": Error: " + webRequest.error);
      }
      else
      {
        var jsonResponse = webRequest.downloadHandler.text;
        var chatJson = JSON.Parse(jsonResponse);
        SetChatHistory(chatJson["render_chat_history"].AsArray);
      }
    }
  }
  #endregion


  #region /// chat ui control
  public void ClearChatHistory()
  {
    foreach (Message message in messageList)
    {
      if (message.textObject != null)
      {
        // Destroy the parent GameObject of the textObject, which is the text bubble
        Destroy(message.textObject.transform.parent.gameObject);
      }
    }
    messageList.Clear();
  }

  public void SetChatHistory(JSONArray chat_history)
  {
    ClearChatHistory();

    foreach (JSONNode chatItem in chat_history)
    {
      string role = chatItem["role"];
      string content = chatItem["content"];

      if (content == "I was gone for a while but i am back now. greetings.") continue;

      Message.MessageType messageType = role == "user" ? Message.MessageType.playerMessage : Message.MessageType.AIMessage;
      SendMessageToChat(content, messageType);
    }
  }

  public Message SendMessageToChat(string text, Message.MessageType messageType)
    {
        
        Message newMessage = new Message();
        GameObject newText;

        newMessage.text = text;
    
        newText = messageType == Message.MessageType.playerMessage? Instantiate(playerTextBubble,chatPanel.transform) : Instantiate(AITextBubble,chatPanel.transform);
        
        newMessage.textObject = newText.GetComponentInChildren<TMP_Text>();

        newMessage.textObject.text = newMessage.text;
        
        messageList.Add(newMessage);

    return newMessage;
    }
    
}

[System.Serializable]
public class Message
{
    public string text;
    public TMP_Text textObject;
    public MessageType messageType;

    public enum MessageType
    {
        playerMessage,
        info,
        AIMessage
        
    }
    
}

#endregion
