// TC2008B. Sistemas Multiagentes y Gr�ficas Computacionales
// C�digo en C# que modifica la visibilidad de un componente en unity.
// Adaptado por Pablo Gonz�lez, Humberto Romero, Valeria Mart�nez y Aleny Ar�valo
// �ltima modificaci�n 21 de Noviembre 2022

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

// Clase que modifica la cantidad de cajas sobre las tarimas
public class TogglePallet : MonoBehaviour
{
    public GameObject caja1, caja2, caja3, caja4, caja5;
    // Start is called before the first frame update
    void Start()
    {
        caja1.SetActive(false);
        caja2.SetActive(false);
        caja3.SetActive(false);
        caja4.SetActive(false);
        caja5.SetActive(false);
    }

    public void AddBox(int contador)
    {
        if (contador == 1)
        {
            caja1.SetActive(true);
        }
        else if (contador == 2)
        {
            caja2.SetActive(true);
        }
        else if (contador == 3)
        {
            caja3.SetActive(true);
        }
        else if (contador == 4)
        {
            caja4.SetActive(true);
        }
        else if (contador == 5)
        {
            caja5.SetActive(true);
        }
    }
}
