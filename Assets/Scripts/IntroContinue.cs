using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class IntroContinue : MonoBehaviour
{
    public void Update()
    {
        if (Input.anyKey)
        {
            SceneManager.LoadScene("Entity");
        } 
    }
}
