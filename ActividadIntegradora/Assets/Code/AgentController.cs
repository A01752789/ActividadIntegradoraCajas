    // TC2008B. Sistemas Multiagentes y Gr�ficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Equipo 4, Noviembre 2022

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

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

public class AgentController : MonoBehaviour
{
    // private string url = "https://agents.us-south.cf.appdomain.cloud/";
    string serverUrl = "http://localhost:8585";
    string getBoxesEndpoint = "/getBoxes";
    string getRobotsEndpoint = "/getRobots";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    RobotsData robotsData;
    BoxesData boxesData;
    Dictionary<string, GameObject> boxes;
    Dictionary<string, GameObject> robots;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;
    bool startedBox = false; 

    public GameObject pallet, pallet1, pallet2, pallet3, pallet4, pallet5, robot, robotCaja, caja, floor;
    public int NAgents, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    // Start is called before the first frame update
    void Start()
    {
        robotsData = new RobotsData();
        boxesData = new BoxesData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        boxes = new Dictionary<string, GameObject>();
        robots = new Dictionary<string, GameObject>();

        width = 15;
        height = 15;

        floor.transform.localScale = new Vector3((float)(width + 1) / 10, 1, (float)(height + 1) / 10);
        //floor.transform.localScale = new Vector3(width, 1, height);
        floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    // Lo primero que se hace desde servidor
    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", (width).ToString());
        form.AddField("height", (height).ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetRobotsData());
            StartCoroutine(GetBoxData());
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

                if (!started)
                {
                    prevPositions[rob.id] = newAgentPosition;
                    robots[rob.id] = Instantiate(robot, newAgentPosition, Quaternion.identity);
                }
                else
                {
                    if (rob.hasBox)
                    {
                        
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

    IEnumerator GetBoxData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getBoxesEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            boxesData = JsonUtility.FromJson<BoxesData>(www.downloadHandler.text);

            Debug.Log(boxesData.positions);

            foreach(BoxData cajita in boxesData.positions)
            {
                if (!startedBox)
                {
                    Vector3 boxPosition = new Vector3(cajita.x, cajita.y, cajita.z);
                    boxes[cajita.id] = Instantiate(caja, boxPosition, Quaternion.identity);
                }
                else
                {
                    if(cajita.picked_up){
                        boxes[cajita.id].SetActive(false);
                    }
                }
            }
            if (!startedBox) startedBox = true;
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
                if(direction != Vector3.zero) robots[rob.Key].transform.rotation = Quaternion.LookRotation(direction);
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
            StartCoroutine(GetBoxData());
        }
    }
}
