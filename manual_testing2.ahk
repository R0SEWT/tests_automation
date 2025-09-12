#SingleInstance, Force
SendMode Event
SetBatchLines, -1

; —————— Configuración ajustable ——————
minCharDelay := 100
maxCharDelay := 700
minLineDelay := 800
maxLineDelay := 2000

pausedFlag := false

; Pausar/reanudar
F8::
    pausedFlag := !pausedFlag
    TrayTip,, % pausedFlag ? "Escritura en pausa" : "Escritura reanudada", 800
return

; Salir
F10::
    TrayTip,, Saliendo…, 800
    ExitApp
return

; Leer y escribir línea a línea
F9::
    ; 1) Selección de archivo
    FileSelectFile, ruta, 3, %A_ScriptDir%, Selecciona un .txt, *.txt
    if (ruta = "") {
        TrayTip,, Cancelado., 800
        return
    }
    if !FileExist(ruta) {
        TrayTip,, No existe: %ruta%, 1500
        return
    }

    ; 2) Leer UTF-8
    contenido := ReadUTF8(ruta)
    if (contenido = "") {
        TrayTip,, Archivo vacío o error de lectura., 1500
        return
    }

    ; 3) Normalizar saltos de línea
    contenido := StrReplace(contenido, "`r`n", "`n")
    contenido := StrReplace(contenido, "`r", "`n")

    ; 4) Guardar ventana activa
    WinGet, prevWinID, ID, A


    ; 5) Bucle de escritura (solo parte con cambios)
        ; usamos StrSplit para dividir exactamente por saltos de línea
    lines := StrSplit(contenido, "`n")
    for index, line in lines
    {
        while (pausedFlag)
            Sleep, 100

        ; parse carácter a carácter SIN usar “,” o “.” como separador
        Loop, Parse, line, "", "" 
        {
 
            while (pausedFlag)
                Sleep, 100

            Sleep, 300                                       
            ControlSend,, a, ahk_id %prevWinID%
            ControlSend,, {BS}, ahk_id %prevWinID% ; borrar el último
            Sleep, 300 
            ch := A_LoopField
            if RegExMatch(ch, "^[{}]$")
                key := ch
            else
                key := "{Text}" ch

            SendWithFallback(key, prevWinID)
            Random, dChar, %minCharDelay%, %maxCharDelay%

            if RegExMatch(ch, "[\.\,\?\!]")
            {
                ; pausa extra tras puntuación
                Random, extraPause, % minLineDelay//2, % minLineDelay
                Sleep, % dChar + extraPause
            }
            else
                Sleep, % dChar
        }

        while (pausedFlag)
            Sleep, 100

        ; sólo aquí enviamos Enter, respetando el salto real del archivo
        SendWithFallback("{Enter}", prevWinID)    ; confirmar linea y empezar a escribir en la sigueinte celda   
        Random, dLine, %minLineDelay%, %maxLineDelay%
        Sleep, % dLine
    }
return


; —————— Funciones auxiliares ——————

; Intenta SendInput, si no funciona usa ControlSend 
SendWithFallback(key, winID := "")
{
    target := winID ? "ahk_id " winID : ""
    ; 1) Intento normal
    if (target)
        ControlSend,, %key%, %target%
    else
        SendInput % key

    Sleep, 800

}

; Lee todo el archivo en UTF-8 (con o sin BOM) al fin
ReadUTF8(path)
{
    try {
        stm := ComObjCreate("ADODB.Stream")
        stm.Type := 2, stm.Charset := "utf-8"
        stm.Open()
        stm.LoadFromFile(path)
        txt := stm.ReadText()
        stm.Close()
        return txt
    } catch e {
        MsgBox, 16, Error de lectura, % "No pude leer `"&path&"`:`n" e.Message
        return ""
    }
}