import { chart } from './drawing.js';
import { parse } from 'mathjs'
import './style.css'
import * as d3 from 'd3'

const inputButton = document.getElementById("input-button")
const inputBox = document.getElementById("input-box")
inputButton.addEventListener("click", function() {
    console.log(inputBox.textContent)
    try {
        const ast = parse(inputBox.textContent)
         console.log(JSON.stringify(ast, null, 2))
         
    } catch (err) {
        inputBox.textContent = err.message
    }  
})

const data = {
  name: "A",
  children: [
    { name: "B", children: [{ name: "C" }, { name: "D" }] },
    { name: "E", children: [{ name: "F" }] },
  ],
};

const { node:node1, g:g1 } = chart(data);
const { node:node2, g:g2 } = chart(data);

document.getElementById('dpll-chart').append(node1);
document.getElementById('cdcl-chart').append(node2);

const zoom1 = d3.zoom()
    .scaleExtent([1, 8])
    .on("zoom", (event) => {
        g1.attr("transform", event.transform)
    });

const zoom2 = d3.zoom()
    .scaleExtent([1, 8])
    .on("zoom", (event) => {
        g2.attr("transform", event.transform)
    });

d3.select(node1).call(zoom1);
d3.select(node2).call(zoom2);