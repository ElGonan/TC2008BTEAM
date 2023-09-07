using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    public float velocidadMovimiento = 5.0f;

    void Update()
    {
        // Obtén la entrada del teclado para el movimiento en los ejes X y Y
        float movimientoHorizontal = Input.GetAxis("Horizontal");
        float movimientoVertical = Input.GetAxis("Vertical");

        // Calcula el desplazamiento en los ejes X y Y
        Vector3 desplazamiento = new Vector3(movimientoHorizontal, movimientoVertical, 0) * velocidadMovimiento * Time.deltaTime;

        // Aplica el desplazamiento a la posición de la cámara
        transform.Translate(desplazamiento);
    }
}