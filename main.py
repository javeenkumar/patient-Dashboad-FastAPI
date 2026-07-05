from fastapi import FastAPI, Path, Query, HTTPException 
import json
import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field 
from typing import List, Dict, Optional, Annotated, Literal


# Pydantic Model
class Address(BaseModel):
    city: Annotated[str, Field(title="City")]
    country: Annotated[str, Field(title="Country")]

class Patient(BaseModel):
    name : Optional[Annotated[str,Field(title='Name',)]]
    age : Optional[Annotated[int,Field(ge=0, le=120, title="Age")]]
    gender :  Optional[Annotated[Literal['Male','Female','Other'],Field(title='Gender')]]
    phone : Optional[Annotated[str,Field(min_length=11, max_length=11)]]
    address :Optional[Address]
    disease : Optional[Annotated[str,Field(title='Disease',)]]
    doctor: Optional[Annotated[str,Field(title='Doctor',)]]
    admit_date :Optional[Annotated[str,Field(title='Admit Date')]]
    status :  Optional[Annotated[Literal['Discharged','Admitted','Under Treatment'],Field(title='Gender')]]


def generate_id(data):
    if not data:
        return "p001"
    
    last_id = sorted(data.keys())[-1]
    num = int(last_id[1:]) + 1
    return f"p{num:03d}"

def loadJson():
    if not os.path.exists("patients.json"):
        return {}

    try:
        with open("patients.json", "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

# Save Json File
def save_json(data):
    with open('patients.json','w')as f:
        json.dump(data,f)

app = FastAPI(
    title="Patient Dashboard",
    description='This dashboard used to manage patient record',
    )

# Used Get Method 
@app.get('/')
def home():
    return{'message':'Wellcome to Dashboad'}

@app.get('/List Patient')
def view_List():
    return loadJson()

# Path Parameter
@app.get('/search/{patient_id}',description='Search By Id')
def search_Patient_by_ID(patient_id:str = Path(..., title= 'ID')):
    if patient_id not in loadJson():
        return {'message':'Invalid Id'}
    else:
        return loadJson()[patient_id]

# Query Parameter
@app.get('/sort')
def Sort_Patient(
    doctorname: str |None = Query(None, description="Filter by Doctor"),
    address: str |None = Query(None, description="Filter by Address"),
    admitdate: str |None = Query(None, description="Filter by Admit Date")
    ):
    data = loadJson()

    result = {}
    for patient_id, patient in data.items():
        
        if doctorname and patient.get('doctor') != doctorname:
            continue

        if address and patient.get("address") != address:
            continue

        if admitdate and patient.get("admit_date") != admitdate:
            continue

        result[patient_id] = patient

    return result
 
#  Post Method
@app.post('/createpatient')
def Create_patient(patient:Patient):

    data = loadJson()
    
    patient_id = generate_id(data)

    for pid, record in data.items():
        if (
            record["name"] == patient.name and
            record["disease"] == patient.disease and
            record["phone"] == patient.phone
        ):
            raise HTTPException(
                status_code=400,
                detail="Patient already exists"
            )
    
    data[patient_id] = patient.model_dump()
    try:
        save_json(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save data: {str(e)}"
        )

    return JSONResponse(status_code= 200, content= patient.model_dump())

# put Method
@app.put('/update')
def Patient_Update(patient_id:str,  patient:Patient):
    data = loadJson()

    if patient_id not in  data:
        raise HTTPException(status_code= 404, detail={'message':'Invalid id'})
    
    existing_data = data[patient_id]

    updating_data = patient.model_dump(exclude_unset=True)

    for key,value in updating_data.items():
        existing_data[key] = value

    
    data[patient_id] = existing_data
    try:
        save_json(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to Update data: {str(e)}"
        )

    return JSONResponse(status_code= 200, content= patient.model_dump())

# Delete Method
@app.delete('/delete/{patient_id}')
def Delete_patient(id:str):
    data = loadJson()

    if id not in data:
        raise HTTPException(
            status_code= 404,
            detail={
                'message':'Unauthorized User'
            }
        )
    else:
        delete_data = data[id]
        del data[id]

        save_json(data)

        return{
            'message':'delete Sucessfully',
            'data': delete_data
        }