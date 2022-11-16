// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
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

    public BoxData(string id, float x, float y, float z)
    {
        this.id = id;
        this.x = x;
        this.y = y;
        this.z = z;
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

        floor.transform.localScale = new Vector3((float)width / 10, 1, (float)height / 10);
        floor.transform.localPosition = new Vector3((float)width / 2 - 0.5f, 0, (float)height / 2 - 0.5f);

        timer = timeToUpdate;

        StartCoroutine(SendConfiguration());
    }

    IEnumerator SendConfiguration()
    {
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());

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
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetObstacleData());
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
