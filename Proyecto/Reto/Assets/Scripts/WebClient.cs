using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class WebClient : MonoBehaviour
{
    private string json; // Debes definir la variable json fuera de los métodos.
    public bool finished = false;
    public string inputString;

    public GameObject floorPrefab; // The prefab for the floor
    public GameObject obstaclePrefab; // The prefab for obstacles
    public GameObject robotCleaners;
    public GameObject Trash;
    public GameObject Papelera;
    public GameObject StartPoint;
    public float spacing = 1.0f; // Spacing between objects


    // IEnumerator - yield return
    IEnumerator SendData(string data)
    {
        while (true) {
            WWWForm form = new WWWForm();
            form.AddField("bundle", "the data");
            string url = "http://localhost:8585";
            using (UnityWebRequest www = UnityWebRequest.Post(url, form))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
                www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
                www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
                www.SetRequestHeader("Content-Type", "application/json");

                yield return www.SendWebRequest();          // Talk to Python
                if (www.isNetworkError || www.isHttpError)
                {
                    Debug.Log(www.error);
                }
                else
                {

                    
                    string result = www.downloadHandler.text; // Get the result
                    Debug.Log(result);
//                    char id_robot = result[0];
//                    char x_position = result[2];
//                   char y_position = result[4];
                    inputString = result;
                    finished = true;
                    // Debug.Log("Finished");

            yield return WaitForThreeSeconds();

        }
    }
}
}
    // Start is called before the first frame update
    void Start()
    {
        
        Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
        json = JsonUtility.ToJson(fakePos); // Asigna el valor de json aquí.
        StartCoroutine(SendData(json));
        finished = false;


    }

    // Update is called once per frame
    void LateUpdate()
    {
        
    }

    IEnumerator WaitForThreeSeconds()
    {
        // StartCoroutine(SendData(json)); // Luego, envía los datos
        yield return new WaitForSeconds(1f); // Espera 3 segundos
        // delete();
        
    }

}
