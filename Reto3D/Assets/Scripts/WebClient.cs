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
    
                    // Debug.Log(result);
                    // char id_robot0 = result[2];
                    // char x_position0 = result[4];
                    // char y_position0 = result[7];
                    // char id_robot1 = result[13];
                    // char x_position1 = result[15];
                    // char y_position1 = result[18];
                    // char id_robot2 = result[24];
                    // char x_position2 = result[26];
                    // char y_position2 = result[29];
                    // char id_robot3 = result[35];
                    // char x_position3 = result[37];
                    // char y_position3 = result[40];
                    // char id_robot4 = result[46];
                    // char x_position4 = result[48];
                    // char y_position4 = result[51];
                    inputString = result;
                    // inputStringTrash = resultTrash;
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
