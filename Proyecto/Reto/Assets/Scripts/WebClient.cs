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
                    string input = www.downloadHandler.text;

                    // Remueve los corchetes externos y divide las filas
                    string[] rows = input.Trim('[', ']').Split(new[] { "], [" }, StringSplitOptions.None);

                    // Inicializa la matriz con el número de filas y columnas adecuado
                    int rowCount = rows.Length;
                    int colCount = rows[0].Split(',').Length;
                    int[,] matriz = new int[rowCount, colCount];

                    // Recorre las filas y elementos para llenar la matriz
                    for (int i = 0; i < rowCount; i++)
                    {
                        string[] elements = rows[i].Split(',');
                        for (int j = 0; j < colCount; j++)
                        {
                            matriz[i, j] = int.Parse(elements[j]);
                        }
                    }


                    // Imprime la matriz
                    for (int i = 0; i < rowCount; i++)
                    {
                        for (int j = 0; j < colCount; j++)
                        {
                            Vector3 position = new Vector3(i * spacing, 1, j * spacing);
                            if (matriz[i,j] == 1)
                            {
                                Vector3 positionTrash = new Vector3(i * spacing, 1, j * spacing) + new Vector3(0, 0f, 0f);
                                Instantiate(robotCleaners, positionTrash, Quaternion.identity);
                                Instantiate(floorPrefab, position, Quaternion.identity);
                            }
                            if (matriz[i,j] == 3)
                            {
                                Vector3 positionObstacle = new Vector3(i * spacing, 1, j * spacing) + new Vector3(0, 5f, 0f);
                                Instantiate(obstaclePrefab, position, Quaternion.identity);
                            }

                            else if (matriz[i,j] == 4)
                            {
                                Vector3 positionPapelera = new Vector3(i * spacing, 1, j * spacing) + new Vector3(0, 0.3f, 0);
                                Instantiate(Papelera, positionPapelera, Quaternion.identity);
                                Instantiate(floorPrefab, position, Quaternion.identity);
                            }
                            else if (matriz[i,j] == 2)
                            {
                                Vector3 positionTrash = new Vector3(i * spacing, 1, j * spacing) + new Vector3(0, 0.8f, 0f);
                                Instantiate(Trash, positionTrash, Quaternion.identity);
                                Instantiate(floorPrefab, position, Quaternion.identity);
                            }
                            else
                            {
                                Instantiate(floorPrefab, position, Quaternion.identity);
                            }
                        }
                    }
                }
            }
            yield return WaitForThreeSeconds();

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
