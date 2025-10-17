import { chart } from './drawing.js';
import { parse } from 'mathjs'
import './style.css'
import * as d3 from 'd3'


const operations = ["¬", "∧", "∨", "→", "↔", "⊕", "⊼", "⊽", "⊙"]
const operationFuncs = [not, and, or, impl, iff, xor, nand, nor, xnor]

// https://mathjs.org/docs/expressions/syntax.html

const operationDictionary = {
    '¬': '-',
    '∧': '/',
    '∨': '%',
    '→': '^',
    '↔': '>',
    '⊕': '&',
    '⊙': './',
    '⊼': '|',
    '⊽': '<'
}

const inverseOperationDictionary = {
    '-': '¬',
    '/': '∧',
    '%': '∨',
    '^': '→',
    '>': '↔',
    '&': '⊕',
    './' : '⊙',
    '|': '⊼',
    '<': '⊽'
}

const invalidChars = ['-', '/', '%', '^', '!', '&', '|', '=', '+']

const keymap = {
    '!' : '¬',
    '@' : '∧',
    '#' : '∨',
    '$' : '→',
    '%' : '↔',
    '^' : '⊕', // xor
    '_' : '⊙', // xnor
    '&' : '⊼', // nand
    '*' : '⊽'  // nor
}


// a ↔ ¬b
function not (a,b) {
    return [[-b, -a], [b, a]]
}
// a ↔ b∧c
function and (a,b,c) {
    return [[b, -a], [c, -a], [-b, -c, a]]
}
// a ↔ b∨c
function or (a,b,c) {
    return [[-b, a], [-c, a], [b, c, -a]]
}
// a ↔ b⊼c
function nand (a,b,c) {
    return [[b, a], [c, a], [-b, -c, -a]]
}
// a ↔ b⊽c
function nor (a,b,c) {
    return [[-b, -a], [-c, -a], [b, c, a]]
}

// a ↔ b⊕c
// return [[b,c,a], [-b,c,-a], [b,-c,-a], [-b,-c,a]] // image
function xor (a,b,c) { // gemini
    return [[b,c,-a], [-b,c,a], [b,-c,a], [-b,-c,-a]]
}

// a ↔ b⊙c // wasnt filled in image
function xnor (a,b,c) {
    return [[-b,-c,a], [b,c,a], [b,-c,-a], [-b,c,-a]]
}
// a ↔ b→c
function impl (a,b,c) {
    return [[-a,-b,c],[b,a],[-c,a]]
}
// a ↔ b↔c
function iff (a,b,c) {
    return xnor(a,b,c)
}

// [Log] {
//   "mathjs": "OperatorNode",
//   "op": "+",
//   "fn": "add",
//   "args": [
//     {
//       "mathjs": "SymbolNode",
//       "name": "a"
//     },
//     {
//       "mathjs": "SymbolNode",
//       "name": "b"
//     }
//   ],
//   "implicit": false,
//   "isPercentage": false
// }

const inputButton = document.getElementById("input-button")
const inputBox = document.getElementById("input-box")

function insertSymbol(symbol) {
    const start = inputBox.selectionStart;
    const end = inputBox.selectionEnd;
    const text = inputBox.value;

    const newvalue = text.substring(0, start) + symbol + text.substring(end)
    inputBox.value = newvalue;
    inputBox.selectionStart = inputBox.selectionEnd = start + symbol.length
}

inputBox.addEventListener("keydown", function(event) {
    if (event.key in keymap) {
        event.preventDefault();
        insertSymbol(keymap[event.key])
    }
})

inputButton.addEventListener("click", function() {
    
    try {

        var text = inputBox.value;

        for (const char of text) {
            if (invalidChars.includes(char)) {
                throw new Error(`character ${char} isn't valid`)
            }
        }

        for (const key in operationDictionary) {
            text = text.replaceAll(key, operationDictionary[key])
        }

        const ast = parse(text)
        if ("value" in ast && ast["value"] === undefined) {
            throw new Error("no input")
        }
        console.log(JSON.stringify(ast, null, 2))
        // traverse bottom-up   
        let inqueue = []
        inqueue.push(ast) // add node to end
        let usedVariables = {}

        // replace the operators with the beautiful ones
        while (inqueue.length > 0) {
            let node = inqueue.shift() // remove node from beginning

            if (node.isOperatorNode) { // we only add operators to outqueue
                node["op"] = inverseOperationDictionary[node["op"]]

                node["args"].forEach((child) => {
                    inqueue.push(child)
                });

            } else if (node.isParenthesisNode) {
                inqueue.push(node["content"])

            } else if (node.isConstantNode) {
                if (!Number.isInteger(node["value"])) {
                    throw new Error(`constant ${node["value"]} isn't an int`)
                }
                usedVariables[Math.abs(parseInt(node["value"]))] = 0 
            } else if (node.isSymbolNode) { // we accept variables with ascii names
                usedVariables[node["name"]] = 0 
            }
        }

        let lastNumber = 0;
        const symbolMappings = {};

        function get_next_number(usedVariables) {
            let iter = lastNumber + 1
            while (iter in usedVariables) { // this is ok because we only add the absolute values to usedVariables.
                iter++;
            }
            lastNumber = iter
            return iter;
        }

        function recursive_substitution(node, substitutionArray) {
            if (node.isOperatorNode) {
                if (node["args"].length == 1) {

                    let a = recursive_substitution(node["args"][0], substitutionArray)

                    if (a in substitutionArray) // if a represents an operatorNode
                        a = substitutionArray[a]

                    let string = `${node["op"]}${a}`
                    substitutionArray[string] = get_next_number(usedVariables)
                    return string

                } else if (node["args"].length == 2) {
                    
                    let a = recursive_substitution(node["args"][0], substitutionArray)
                    let b = recursive_substitution(node["args"][1], substitutionArray)

                    if (a in substitutionArray) // if a represents an operatorNode
                        a = substitutionArray[a]

                    if (b in substitutionArray) // if b represents an operatorNode
                        b = substitutionArray[b]
                   
                    let string = `${a}${node["op"]}${b}`
                    substitutionArray[string] = get_next_number(usedVariables)
                    return string
                }
            } else if (node.isParenthesisNode) {
                return recursive_substitution(node["content"], substitutionArray) // maybe has an operatorNode inside
            } else if (node.isConstantNode) { // the return values are used to return strings, the strings are then converted to numbers using 'substitutionArray'
                return node["value"]
            } else if (node.isSymbolNode) {
                let number = get_next_number(usedVariables)
                symbolMappings[node["name"]] = number
                return number
            }
        }

        const substitutionArray = {};
        recursive_substitution(ast, substitutionArray);

        console.log(substitutionArray)    
        console.log(symbolMappings)

        const tseitin = Object.entries(substitutionArray).flatMap(([key, outputVar]) => {
            const opIndex = operations.findIndex(op => key.includes(op))
            const operands = key.split(operations[opIndex]).filter(s => s.trim() !== '').map(s => parseInt(s))
            return operationFuncs[opIndex](outputVar, ...operands)
        });    

        console.log(tseitin)

    } catch (err) {
        inputButton.innerText = err.message
        setTimeout(()=>{
            inputButton.innerText = "calculate"
        }, 2000)
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