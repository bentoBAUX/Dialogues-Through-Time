using System;
using System.Collections;
using System.Text;
using System.Collections.Generic;
using TMPro;
using UnityEditor.VersionControl;
using UnityEngine;
using UnityEngine.Serialization;
using UnityEngine.UI;

using UnityEngine.Networking;
using SimpleJSON;


public class ChatManager : MonoBehaviour
{
    public GameObject chatPanel;
    
    public GameObject playerTextBubble;

    public GameObject AITextBubble;

    
    public TMP_InputField chatBox;

    [SerializeField] private bool playerSent = false;
    
    [SerializeField]
    private List<Message> messageList = new List<Message>();

    private string uniqueId = "";
    private string serverUrl = "http://127.0.0.1:5000"; 
    private bool processing = false;

    void Start()
    {
      //get id
      LoadUniqueId();
      FetchAndSetChatHistory();
    }



  void Update()
  {
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
      LoadUniqueId();
      ClearChatHistory();
    }
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
    using (UnityWebRequest webRequest = UnityWebRequest.Get(serverUrl + "/get_unique_id"))
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
    return $"{serverUrl}/chat";
  }

  IEnumerator PostChatStream(string message)
  {
    if (processing)
		{
      Debug.LogError("Message from ai already processing");
      yield break;
		}

    //init
    processing = true;
    chatBox.text = "";
    SendMessageToChat(message, Message.MessageType.playerMessage);

    // Create a JSON object and add the message with proper escaping
    var jsonNodeSend = new JSONObject();
    jsonNodeSend.Add("user_msg", new JSONString(message));
    jsonNodeSend.Add("unique_id", new JSONString(GetSavedUniqueId()));

    // Convert the JSON object to a string, which will be properly escaped
    string jsonData = jsonNodeSend.ToString();
    byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonData);

    // Create a POST UnityWebRequest
   using (UnityWebRequest request = new UnityWebRequest(GetChatUrl(), "POST"))
    {
      request.uploadHandler = new UploadHandlerRaw(bodyRaw);
      request.downloadHandler = new DownloadHandlerBuffer();
      request.SetRequestHeader("Content-Type", "application/json");

      // Send the request
      request.SendWebRequest();

      bool streamEnded = false;
      string lastResponse = "";

      //create message box
      Message messageBox = SendMessageToChat("", Message.MessageType.AIMessage);

      //start adding text to the message box
      while (!streamEnded)
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
            string newData = response.Substring(lastResponse.Length);
            if (!string.IsNullOrEmpty(newData))
            {
              //we get the json response from the server
              var chatJson = JSON.Parse(newData);
              if (chatJson.HasKey("ai_speaking"))
              {
                string aiResponse = chatJson["ai_speaking"];
                Debug.Log(aiResponse);
                messageBox.text = aiResponse;
                messageBox.textObject.text = aiResponse;
              }

              Debug.Log(chatJson);

              //end streaming if json says it
              streamEnded = chatJson.HasKey("streaming");

              ///Things that happen after finishes talking
              //set chat history
              if (streamEnded && chatJson.HasKey("render_chat_history")) SetChatHistory(chatJson["render_chat_history"].AsArray);

              //end conversation and change scene
              if (streamEnded && chatJson["end_reason"] == "end_conversation")
							{
                Debug.Log("Scene should change to " + chatJson["current_scene"]);
                //TODO: make transition, change scene
							}
            }

            lastResponse = response;
          }
        }

        // Wait before checking for more data
        yield return new WaitForSeconds(0.2f);
      }

      processing = false;
      Debug.Log("end");
    }
  }

  public void FetchAndSetChatHistory()
  {
    StartCoroutine(GetChatHistoryCoroutine());
  }

  private IEnumerator GetChatHistoryCoroutine()
  {
    string url = $"{serverUrl}/chat_history/{GetSavedUniqueId()}";
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
        Destroy(message.textObject.gameObject);
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
