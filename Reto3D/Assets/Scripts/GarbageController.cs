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
    public GameObject Starting;
    public GameObject Desconocido;
    public float spacing = 1.0f;

    private Dictionary<string, GameObject> robots = new Dictionary<string, GameObject>();
    private string url = "http://localhost:8586";

    void Start()
    {
        StartCoroutine(FetchGarbageData());
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
                            if (int.TryParse(elements[j], out int number))
                            {
                                matriz[i, j] = number;
                            }
                        }
                    }
                    
                    // Imprime matriz 
                    for (int i = 0; i < rowCount; i++)
                    {
                        
                        for (int j = 0; j < colCount; j++)
                        {
                            Debug.Log(matriz[i, j]);

                            Vector3 position = new Vector3(i * spacing, j * spacing, 0);
                            if (matriz[i, j] >= 1 && matriz[i, j] <= 9)
                            {
                                Vector3 positionGarbage = position + new Vector3(0, 0, 0);
                                Instantiate(Garbage, position, Quaternion.identity);

                            }
                            else if (matriz[i, j] == -1)
                            {
                                Vector3 positionStarting = position + new Vector3(0, 0, 0);
                                Instantiate(Starting, position, Quaternion.identity);
                                Debug.Log("Starting");
                            }

                            else if (matriz[i, j] == -2)
                            {
                                Vector3 positionBote = position + new Vector3(0, 0, 0);
                                Instantiate(Bote, position, Quaternion.identity);
                                Debug.Log("Bote");
                            }
                            else if (matriz[i, j] == -3)  // Usando la constante definida
                            {
                                Vector3 positionObsta = position + new Vector3(0, 0, 0);
                                Instantiate(Obsta, position, Quaternion.identity);
                            }
                            
                            

                        }
                    }
                }
                
            }
            yield return new WaitForSeconds(1f);
            delete();
        }
    }

    IEnumerator WaitForThreeSeconds()
    {
        // StartCoroutine(SendData(json)); // Luego, envía los datos
        yield return new WaitForSeconds(1f); // Espera 3 segundos
        // delete();

    }

    void delete()
    {

        GameObject[] obstacles = GameObject.FindGameObjectsWithTag("Obstaculos");
        foreach (GameObject obstacle in obstacles)
        {
            WaitForThreeSeconds();
            Destroy(obstacle);
        }
        GameObject[] floors = GameObject.FindGameObjectsWithTag("Piso");
        foreach (GameObject floor in floors)
        {
            WaitForThreeSeconds();
            Destroy(floor);
        }
        GameObject[] trash = GameObject.FindGameObjectsWithTag("Basura");
        foreach (GameObject trash1 in trash)
        {
            WaitForThreeSeconds();
            Destroy(trash1);
        }
        GameObject[] papeleras = GameObject.FindGameObjectsWithTag("Bote");
        foreach (GameObject papelera in papeleras)
        {
            WaitForThreeSeconds();
            Destroy(papelera);
        }
        GameObject[] Starting = GameObject.FindGameObjectsWithTag("Starting");
        foreach (GameObject start in Starting)
        {
            WaitForThreeSeconds();
            Destroy(start);
        }

    }

}