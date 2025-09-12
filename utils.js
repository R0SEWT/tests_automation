function certDistHor(selIzq, selDer) { 
    const elA = document.querySelector(selIzq);
    const elB = document.querySelector(selDer);
  
    if (!elA) {
      console.error("Not find izq:", selIzq); 
      return null;
    }
  
    if (!elB) {
      console.error("Not find der:", selDer); 
      return null;
    }
  
    const rectA = elA.getBoundingClientRect();
    const rectB = elB.getBoundingClientRect();
  
    const distancia = rectB.left - rectA.right;
    console.log("Distancia:", distancia);
    return distancia;
}

    

function certDistVert(selUp, selDown) { 
    const elA = document.querySelector(selUp);
    const elB = document.querySelector(selDown);
  
    if (!elA) {
      console.error("Not find izq:", selUp); 
      return null;
    }
  
    if (!elB) {
      console.error("Not find der:", selDown); 
      return null;
    }
  
    const rectA = elA.getBoundingClientRect();
    const rectB = elB.getBoundingClientRect();
  
    const distancia = rectB.bottom - rectA.up;
    console.log("Distancia vertical:", distancia);
    return distancia;
}

function certDistToEndScreen(selector) {
  const el = document.querySelector(selector);

  if (!el) {
    console.error("No se encontró el selector:", selector);
    return null;
  }

  const rect = el.getBoundingClientRect();
  const distancia = window.innerHeight - rect.bottom;
  console.log("Distancia al final de la pantalla:", distancia);
  return distancia;
}
  