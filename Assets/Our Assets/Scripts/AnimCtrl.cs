using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AnimCtrl : MonoBehaviour
{
    private Animator _animator;

    public void Start()
    {
        _animator = this.gameObject.GetComponent<Animator>();
    }

    public void Talk()
    {
        _animator.SetTrigger("talkTrigger");
    }

    public void Idle()
    {
        _animator.SetTrigger("idleTrigger");
    }
}
