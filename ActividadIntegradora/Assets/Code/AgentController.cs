// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// Código en C# que interactúa con el servidor en Python. Basado en el código de Sergio Ruiz.
// Adaptado por Pablo González, Humberto Romero, Valeria Martínez y Aleny Arévalo
// Última modificación 21 de Noviembre 2022

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

// Clase del agente robot para inicializarlo
[Serializable]
public class RobotData
{
    public string id;
    public float x, y, z;
    public bool hasBox;

    public RobotData(string id, float x, float y, float z, bool hasBox)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.hasBox = hasBox;
    }
}

[Serializable]
public class RobotsData
{
    public List<RobotData> positions;

    public RobotsData() => this.positions = new List<RobotData>();
}


// Clase del agente caja para inicializarlo
[Serializable]
public class BoxData
{
    public string id;
    public float x, y, z;
    public bool picked_up;

    public BoxData(string id, float x, float y, float z, bool picked_up)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.picked_up = picked_up;
    }
}

[Serializable]
public class BoxesData
{
    public List<BoxData> positions;

    public BoxesData() => this.positions = new List<BoxData>();
}

// Clase del agente tarima para inicializarlo
[Serializable]
public class PalletData
{
    public string id;
    public float x, y, z;
    public int value;

    public PalletData(string id, float x, float y, float z, int value)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
        this.value = value;
    }
}

[Serializable]
public class PalletsData
{
    public List<PalletData> positions;

    public PalletsData() => this.positions = new List<PalletData>();
}

// Clase que controla el movimiento y visualización de los agentes
public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    string getBoxesEndpoint = "/getBoxes";
    string getRobotsEndpoint = "/getRobots";
    string getPalletsEndpoint = "/getPallets";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    RobotsData robotsData;
    BoxesData boxesData;
    PalletsData palletsData;
    Dictionary<string, GameObject> boxes;
    Dictionary<string, GameObject> robots;
    Dictionary<string, GameObject> pallets;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;
    bool startedBox = false, startedPallet = false;

    public GameObject pallet, robot, caja, floor;
    public int NBoxes, width, height, maxSteps;
    public float timeToUpdate;
    private float timer, dt;

    void Start()
    {
        robotsData = new RobotsData();
        boxesData = new BoxesData();
        palletsData = new PalletsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        boxes = new Dictionary<string, GameObject>();
        robots = new Dictionary<string, GameObject>();
        pallets = new Dictionary<string, GameObject>();

        // Escalar y posicionar piso
        floor.transform.localScale = new Vector3((float)(width + 1) / 10, 1, (float)(height + 1) / 10);
        floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    // Lo primero que se hace desde servidor
    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NAgents", (NBoxes).ToString());
        form.AddField("width", (width).ToString());
        form.AddField("height", (height).ToString());
        form.AddField("maxSteps", (maxSteps).ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        // Empezar simulación si hay conexión exitosa
        else
        {
            //Debug.Log("Configuration upload complete!");
            //Debug.Log("Getting Agents positions");
            StartCoroutine(GetRobotsData());
            StartCoroutine(GetBoxesData());
            StartCoroutine(GetPalletsData());
        }
    }

    IEnumerator GetRobotsData()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getRobotsEndpoint);
        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else
        {
            robotsData = JsonUtility.FromJson<RobotsData>(www.downloadHandler.text);

            foreach (RobotData rob in robotsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(rob.x, rob.y, rob.z);

                // Instanciar robots
                if (!started)
                {
                    prevPositions[rob.id] = newAgentPosition;
                    robots[rob.id] = Instantiate(robot, newAgentPosition, Quaternion.identity);
                }
                // Si el robot ya existe, modificar su comportamiento y apariencia
                else
                {
                    // Si tiene caja, cambiar prefab y quitar luz
                    if (rob.hasBox)
                    {
                        robots[rob.id].GetComponent<ToggleBox>().AddBox();
                    }
                    else
                    {
                        robots[rob.id].GetComponent<ToggleBox>().RemoveBox();
                    }
                    Vector3 currentPosition = new Vector3();
                    if (currPositions.TryGetValue(rob.id, out currentPosition))
                        prevPositions[rob.id] = currentPosition;
                    currPositions[rob.id] = newAgentPosition;
                }
            }

            updated = true;
            if (!started) started = true;
        }
    }

    IEnumerator GetBoxesData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            boxesData = JsonUtility.FromJson<BoxesData>(www.downloadHandler.text);

            //Debug.Log(boxesData.positions);

            foreach(BoxData cajita in boxesData.positions)
            {
                // Instanciar cajas
                if (!startedBox)
                {
                    Vector3 boxPosition = new Vector3(cajita.x, cajita.y, cajita.z);
                    boxes[cajita.id] = Instantiate(caja, boxPosition, Quaternion.identity);
                }
                // Si la caja ya existe, modificar su visibilidad de acuerdo a su estado
                else
                {
                    // Si un robot tomó la caja, ya no se muestra en el plano
                    if(cajita.picked_up){
                        boxes[cajita.id].SetActive(false);
                    }
                }
            }
            if (!startedBox) startedBox = true;
        }
    }

    IEnumerator GetPalletsData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getPalletsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            palletsData = JsonUtility.FromJson<PalletsData>(www.downloadHandler.text);

            foreach(PalletData tarima in palletsData.positions)
            {
                // Instanciar tarimas
                if (!startedPallet)
                {
                    Vector3 palletPosition = new Vector3(tarima.x, tarima.y, tarima.z);
                    pallets[tarima.id] = Instantiate(pallet, palletPosition, Quaternion.identity);
                }
                else
                {
                    // Si se le añade una caja al pallet en mesa, añadir caja en prefab
                    pallets[tarima.id].GetComponent<TogglePallet>().AddBox(tarima.value);
                }
            }
            if (!startedPallet) startedPallet = true;
        }
    }


    private void Update() 
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            foreach(var rob in currPositions)
            {
                Vector3 currentPosition = rob.Value;
                Vector3 previousPosition = prevPositions[rob.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                robots[rob.Key].transform.localPosition = interpolated;
                // Cambiar hacia dónde miran los robots dependiendo de su posición y dirección
                if (direction != Vector3.zero) robots[rob.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
        }
    }

    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetRobotsData());
            StartCoroutine(GetBoxesData());
            StartCoroutine(GetPalletsData());
        }
    }
}
