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
    
    public GameObject playerTextBubble;

    public GameObject AITextBubble;

    
    public TMP_InputField chatBox;

    [SerializeField] private bool playerSent = false;
    
    [SerializeField]
    private List<Message> messageList = new List<Message>();
 

    void Update()
    {
        if (chatBox.text != "")
        {
            if (Input.GetKeyDown(KeyCode.Return))
            {
                SendMessageToChat(chatBox.text, Message.MessageType.playerMessage);
                chatBox.text = "";
                playerSent = true;
            }
        }
        else
        {
            if (!chatBox.isFocused && Input.GetKeyDown(KeyCode.Return))
            {
                chatBox.ActivateInputField();
            }
        }

        if (playerSent)
        {
            SendMessageToChat("At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat",Message.MessageType.AIMessage);
            playerSent = false;
        }
    }

    public void SendMessageToChat(string text, Message.MessageType messageType)
    {
        
        Message newMessage = new Message();
        GameObject newText;

        newMessage.text = text;
    
        newText = messageType == Message.MessageType.playerMessage? Instantiate(playerTextBubble,chatPanel.transform) : Instantiate(AITextBubble,chatPanel.transform);
        
        newMessage.textObject = newText.GetComponentInChildren<TMP_Text>();

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
