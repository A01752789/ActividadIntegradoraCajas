using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ToggleBox : MonoBehaviour
{
    public GameObject Box;
    public Light Luz;
    private Color verde = new Color(39, 255, 0);
    private Color rojo = new Color(255, 14, 0);
    
    // Start is called before the first frame update
    void Start()
    {
        Box.SetActive(false);
        Luz.color = verde;
    }

    public void RemoveBox()
    {
        Box.SetActive(false);
        Luz.color = verde;
    }

    public void AddBox()
    {
        Box.SetActive(true);
        Luz.color = rojo;
    }
}
