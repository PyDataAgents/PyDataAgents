/**
* returns an array with unique elements based on values of {@code values}
* in ascending numerical order
* @param values
* @return
*/
function unique(values){
    return values.filter((x, i, a) => a.indexOf(x) == i).sort();
}

/**
 * searches the indices in {@code values}, where the element of {@code values} is equal to {@code value}
 * <br>if no element is found an empty array is returned
 * @param values
 * @param value
 * @return
 */
function find(values, value){
    let foundIndices = new Array();
    for (let i = 0; i < values.length; i++){
        if (values[i] == value){
        foundIndices.push(i);
        }
    }
    return foundIndices;
}

/**
 * returns the elements at indices {@code indices} in {@code values} into new array
 * @param values
 * @param indices
 * @return Array()
 */
function elementsAt(values, indices){
    let newValues = new Array();
    for (let i = 0; i < indices.length; i++){
        newValues.push(values[indices[i]]);
    }
    return newValues;
}

/**
 * groups the {@code values} by {@code indices} to a new double matrix where each row represents all values corresponding to each unique index found in {@code indices}
 * 
 * @param values
 * @param indices
 * @return
 */
function group(values, indices){
    let ui = unique(indices);
    let valueAr = new Array();
    for (let i = 0; i < ui.length; i++){
        let thisIndex = ui[i];
        let gi = find(indices, thisIndex);
        let gv = elementsAt(values, gi);
        //console.log(gi);
        //console.log(gv);
        valueAr.push(gv);
    }
    return valueAr;
}

// retrieve data from datasource and create a cluster plot based on 
// 2D or 3D data and a cluster index
//console.log(data);
let count = data.series[0].fields[1].values.length;
let x = data.series[0].fields[1].values[0];
let y = data.series[0].fields[1].values[1];
let z = null;
let c = null;
if (count == 3){
    c = data.series[0].fields[1].values[2];
} else if (count == 4){
    z = data.series[0].fields[1].values[2];
    c = data.series[0].fields[1].values[3]; 
} else {
    console.error("Unknown Data Format in data, cannot generate cluster plot");
}

// parse string arrays to number arrays
let xd = JSON.parse(x);
let yd = JSON.parse(y);
let ci = JSON.parse(c);
let zd = null;
if (count == 4){
    zd = JSON.parse(z);
}
//console.log(xd);
//console.log(yd);
//console.log(zd);
//console.log(ci);
//console.log(unique(ci));

// iterate over cluster indices and create traces for each group
let cu = unique(ci);
let xg = group(xd, ci);
let yg = group(yd, ci);
let zg = null;
if (zd != null){
    zg = group(zd, ci);
}
console.log(cu);
console.log(xg);

let pData = [];

for (let i = 0; i < cu.length; i++){
    let trace = {};
    trace.x = xg[cu[i]];
    trace.y = yg[cu[i]];
    if (zg != null){
        trace.z = zg[cu[i]];
    }
    if (zg != null){
        trace.type = "scatter3d";
    } else {
        trace.type = "scatter";
    }
    trace.mode = "markers";
    pData.push(trace);
}

console.log(pData);

if (zg != null){  
    return {
        data: pData,
        layout: {
            xaxis: { title: "X" },
            yaxis: { title: "Y" },
            zaxis: {title: "Z"}
        }  
    }
} else {
    return {
        data: pData,
        layout: {
            xaxis: { title: "X" },
            yaxis: { title: "Y" }
        }  
    }
}
