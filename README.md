# BB algorithms for selection of functional split
Functional Splitting Algorithms in Python. 
This tries to improve previous algorithms implemented in the following [Git Repository](https://github.com/cristian-erazo/Joint_Route_Selection_and_Split_Level_Management_for_5G_C-RAN)

## Overall problem description

The solver will find a stuitable solution for functional split placement optimizinf an objective function and subjected to physical constraints. So far the objective function aims to maximize the centralization. The constraints take into account the desired placement of the base stations and the requirements of the potential splits in terms of: required bandwidth CU-DU, required delay CU-DU, required computational capacity for CU and DU. 

## Parameters configuration

### Functional splits
The requirements of the functional splits is described in **params.csv**. The columns indicate:
+ *SPLIT*: name fo the functional split
+ *PRB*: number of PRBs (bandwidth) of the bsae station
+ *DR*: minimum required DR between the CU and DU in **Mbps**
+ *DELAY*: maximum required delay in **ms** for the functional split
+ *CU_CAP*: computational capacity in **GOPS** required by the CU for the functional-split/PRBs
+ *DU_CAP*: computational capacity in **GOPS** required by the DU for the functional-split/PRBs
