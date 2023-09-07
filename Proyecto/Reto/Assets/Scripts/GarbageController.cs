using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using System;

public class GarbageController : MonoBehaviour
{

    public GameObject Garbage;
    public GameObject floorPrefab;
    public GameObject Obsta;
    public GameObject Bote;
    public GameObject Startingpoint;
    public GameObject Desconocido;
    public float spacing = 0.5f;

    private Dictionary<string, GameObject> robots = new Dictionary<string, GameObject>();
    private string url = "http://localhost:8585";

    void Start()
    {
        FetchGarbageData();
    }

    IEnumerator FetchGarbageData()
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
                    // Imprime matriz 
                    for (int i = 0; i < rowCount; i++)
                    {
                        for (int j = 0; j < colCount; j++)
                        {
                            Vector3 position = new Vector3(i * spacing, 1, j * spacing);
                            if (matriz[i, j] == -3)  // Usando la constante definida
                            {
                                Vector3 positionObstacle = position + new Vector3(0, 5f, 0f);
                                Instantiate(obstaclePrefab, positionObstacle, Quaternion.identity);
                            }
                            else if (matriz[i, j] == -2)
                            {
                                Vector3 positionBote = position + new Vector3(0, 0.3f, 0);
                                Instantiate(Papelera, positionPapelera, Quaternion.identity);

                            }
                            else if (matriz[i, j] >= 1 && matriz[i, j] <= 9)
                            {
                                Vector3 positionGarbage = position + new Vector3(0, 0.8f, 0f);
                                Instantiate(Garbage, positionGarbage, Quaternion.identity);

                            }
                            else if (matriz[i, j] == -1)
                            {
                                Instantiate(StartPrefab, position, Quaternion.identity);
                            }
                            else if (matriz[i, j] == -5)
                            {
                                Vector3 positionUnknown = position + new Vector3(0, 5f, 0f);
                                Instantiate(UnknownPrefab, positionUnknown, Quaternion.identity);
                            }
                        }
                    }
                }
            }
            yield return new WaitForSeconds(1);
       }
    }
}