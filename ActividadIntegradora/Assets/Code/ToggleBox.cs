// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// Código en C# que modifica la visibilidad del agente robot.
// Adaptado por Pablo González, Humberto Romero, Valeria Martínez y Aleny Arévalo
// Última modificación 21 de Noviembre 2022

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// Clase que modifica la visibilidad de las cajas y luces sobre los agentes
public class ToggleBox : MonoBehaviour
{
    public GameObject Box;
    public Light Luz;
    
    void Start()
    {
        Box.SetActive(false);
        Luz.color = Color.green;
    }

    public void RemoveBox()
    {
        Box.SetActive(false);
        Luz.color = Color.green;
    }

    public void AddBox()
    {
        Box.SetActive(true);
        Luz.color = Color.red;
    }
}
