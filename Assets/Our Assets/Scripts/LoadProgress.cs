using SimpleJSON;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.SceneManagement;

public class NewBehaviourScript : MonoBehaviour
{
  // Start is called before the first frame update
  void Start()
  {
		Screen.SetResolution(Screen.currentResolution.width, Screen.currentResolution.height, true);
		string uniqueId = PlayerPrefs.GetString("UniqueID", "");

    if (!string.IsNullOrEmpty(uniqueId))
    {
      Debug.Log("Loaded saved Unique ID: " + uniqueId);
      StartCoroutine(LoadProgressCall(uniqueId));
    }
  }

  private IEnumerator LoadProgressCall(string uniqueId)
  {
    string url = $"{Utilities.serverUrl}/chat_history/{uniqueId}";
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
        if (Utilities.sceneMap.TryGetValue(chatJson["current_scene"], out string value))
        {
          SceneManager.LoadScene(value);
        }
        else
        {
          Debug.LogError("Scene from server doesnt exist!" + chatJson["current_scene"]);
        }
      }
    }
  }

  // Update is called once per frame
  void Update()
  {
        
  }
}
