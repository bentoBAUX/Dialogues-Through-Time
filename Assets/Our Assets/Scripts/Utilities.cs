using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Utilities : MonoBehaviour
{
  public static string serverUrl = "https://dialoguesthroughtime.azurewebsites.net";

  public static  Dictionary<string, string> sceneMap = new Dictionary<string, string>()
  {
    {"entity", "Entity"},
    {"entity_test", "Entity"},
    {"socrates", "Socrates" },
    {"jesus", "Jesus" },
    {"leonardo","LeoDaVinci" }
  };

  // Start is called before the first frame update
  void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
