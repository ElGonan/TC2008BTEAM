using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class RobotController : MonoBehaviour
{
    public GameObject RobotPrefab;
    private Dictionary<string, GameObject> robots = new Dictionary<string, GameObject>();
    private string url = "http://localhost:8585";

    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(FetchRobotData());
    }

    // Coroutine to fetch robot data
    IEnumerator FetchRobotData()
    {
        while (true)
        {
            WWWForm form = new WWWForm();
            form.AddField("bundle", "the data");
            using (UnityWebRequest www = UnityWebRequest.Post(url, form))
            {
                yield return www.SendWebRequest();

                if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
                {
                    Debug.Log(www.error);
                }
                else
                {
                    string result = www.downloadHandler.text; // Get the result
                    OnReceiveData(result);
                }
            }
            yield return new WaitForSeconds(1); // wait for a second before fetching again
        }
    }

public void OnReceiveData(string result)
{
    result = result.Trim('[', ']');
    string[] robotDataArray = result.Split(new string[] { ")', '" }, StringSplitOptions.None);

    foreach (string robotData in robotDataArray)
    {
        string cleanedData = robotData.Trim('\'');
        string[] parts = cleanedData.Split('(');


        
        if (parts.Length != 2) continue;

        string id = parts[0];
        string coords = parts[1].Trim(')', ' ');

        string[] xy = coords.Split(',');
  
        
        if (xy.Length != 2) continue;

        if (float.TryParse(xy[0], out float x) && float.TryParse(xy[1], out float y))
        {
             // Debug to check x and y

            // Si el robot con este ID no existe, lo creamos
            if (!robots.ContainsKey(id))
            {
                GameObject newRobot = Instantiate(RobotPrefab);
                robots.Add(id, newRobot);
            }

            // Actualizamos la posición del robot
            GameObject robot = robots[id];
            robot.transform.position = new Vector3(x, y - 0.3f, 0);
            }
            
    }
}

}