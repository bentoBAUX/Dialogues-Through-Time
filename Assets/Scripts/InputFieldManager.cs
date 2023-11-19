using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public class InputFieldManager : MonoBehaviour
{
    [SerializeField]
    private bool _isPlaceholderHideOnSelect;


    [SerializeField]
    private TMP_InputField _inputField;


    public void OnInputFieldSelect()
    {
        if (this._isPlaceholderHideOnSelect == true)
        {
            this._inputField.placeholder.gameObject.SetActive(false);
        }
    }

    public void OnInputFieldDeselect()
    {
        if (this._isPlaceholderHideOnSelect == true)
        {
            this._inputField.placeholder.gameObject.SetActive(true);
        }
    }
}
