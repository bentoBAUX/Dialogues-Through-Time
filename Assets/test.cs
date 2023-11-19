using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;


public class test : MonoBehaviour
{
    private string uniqueId = "";
    private string serverUrl = "http://127.0.0.1:5000"; // Replace with your server URL
    private string chatMsg = "hi";

    void Start()
    {
        //get id
        LoadUniqueId();

    }

    void Update()
    {
        // Check if the Enter key is pressed and uniqueId is not empty
        if (Input.GetKeyDown(KeyCode.Return) && !string.IsNullOrEmpty(uniqueId))
        {
            // Start the coroutine to read the stream
            StartCoroutine(ReadStream(uniqueId));
        }
    }

    /// get ID
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

    //stream
   private string GetChatUrl(string uniqueId)
    {
        return $"{serverUrl}/chat/{uniqueId}?user_msg={UnityWebRequest.EscapeURL(chatMsg)}";
    }

    IEnumerator ReadStream(string id)
    {
      string urlWithParams = GetChatUrl(id);
      string lastResponse = "";
      Debug.Log(urlWithParams);  

      using (UnityWebRequest request = UnityWebRequest.Get(urlWithParams))
      {
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SendWebRequest();

        while (!request.isDone)
        {
          if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
          {
            Debug.LogError("Error: " + request.error);
            yield break;
          }
				  // Check if the server is reachable or not
				  if (request.responseCode == 404 || request.responseCode == 0)
				  {
					  Debug.LogError("Server not found or unreachable.");
					  yield break;
				  }

				  string currentResponse = request.downloadHandler.text;
          if (currentResponse != lastResponse)
          {
            string newData = currentResponse.Substring(lastResponse.Length);
            ProcessStreamData(newData);
            lastResponse = currentResponse;
          }

          yield return new WaitForSeconds(0.4f); // Wait for a second before checking for new data
        }
      }
    }




    private void ProcessStreamData(string data)
    {
        if (!string.IsNullOrEmpty(data))
        {
            Debug.Log("Stream Data: " + data);
            // Here you can add your logic to process each piece of data
        }
    }
}
