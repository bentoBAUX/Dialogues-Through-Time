using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEditor.VersionControl;
using UnityEngine;
using UnityEngine.Serialization;
using UnityEngine.UI;

public class ChatManager : MonoBehaviour
{
    public GameObject chatPanel;
    public GameObject playerTextObject;
    public GameObject AITextObject;
    public TMP_InputField chatBox;
    
    
    [SerializeField]
    private List<Message> messageList = new List<Message>();
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (chatBox.text != "")
        {
            if (Input.GetKeyDown(KeyCode.Return))
            {
                SendMessageToChat(chatBox.text, Message.MessageType.playerMessage);
                chatBox.text = "";
            }
        }
        else
        {
            if (!chatBox.isFocused && Input.GetKeyDown(KeyCode.Return))
            {
                chatBox.ActivateInputField();
            }
        }
    }

    public void SendMessageToChat(string text, Message.MessageType messageType)
    {
        
        Message newMessage = new Message();
        GameObject newText;

        newMessage.text = text;
    
        newText = messageType == Message.MessageType.playerMessage? Instantiate(playerTextObject,chatPanel.transform) : Instantiate(AITextObject,chatPanel.transform);
        
        newMessage.textObject = newText.GetComponent<TMP_Text>();

        newMessage.textObject.text = newMessage.text;
        
        messageList.Add(newMessage);
        
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
