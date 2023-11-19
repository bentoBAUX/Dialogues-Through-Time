using System;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;

public class Chat : MonoBehaviour
{
    public TMP_Text messageSent;
    private bool _isPlaceholderHideOnSelect;
    private string _input;

    
    [SerializeField]
    private TMP_InputField _inputField;



    public void ReadStringInput()
    {
        
        messageSent.SetText(_inputField.text);
        _inputField.text = "";
        
    }
    
    
}
