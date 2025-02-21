# Cart-Pole Optimal Control Assignment

[Watch my video](https://drive.google.com/file/d/1rPaYaQFi7gwk5XYfn2aMJvr7oC3SJ-R5/view?usp=sharing)

![cart pole](https://github.com/user-attachments/assets/229dcbe6-1ea9-4a90-8e1d-a0ac7fadadcc)


## Introduction
The cart-pole system is a classic underactuated system where a pendulum is balanced on a moving cart. The system faces external disturbances, in this case, earthquake-like forces, requiring a well-tuned Linear Quadratic Regulator (LQR) for stabilization.

This assignment involves:

1. Tuning the LQR controller to maintain balance.
2. Ensuring cart position remains within ±2.5m.
3. Testing system performance under disturbances.
4. Logging performance metrics like pole angle deviation, cart displacement, and control effort.

### Physical Setup
- Inverted pendulum mounted on a cart
- Cart traversal range: ±2.5m (total range: 5m)
- Pole length: 1m
- Cart mass: 1.0 kg
- Pole mass: 1.0 kg

### Disturbance Generator
The system includes an earthquake force generator that introduces external disturbances:
- Generates continuous, earthquake-like forces using superposition of sine waves
- Base amplitude: 15.0N (default setting)
- Frequency range: 0.5-4.0 Hz (default setting)
- Random variations in amplitude and phase
- Additional Gaussian noise

## Assignment Objectives

### Core Requirements
1. After multiple tests, we tuned Q and R for better stability:
   Q = [50.0, 5.0, 100.0, 20.0]  # Improved state cost
   
   R = [0.1] # Reduced control force magnitude
   
## 2. LQR Tuning Approach
   Q[0,0] = 1.0 → Low weight on cart position → Allowed excessive cart displacement.
   Q[2,2] = 10.0 → Penalized pole angle deviations but not strong enough.
   R = 0.1 → Allowed aggressive control efforts.
   
   ## Issues Observed:
   Large cart displacements (~3m).
   Oscillatory control behavior.
   Pendulum instability under strong earthquake forces.

## Justification for LQR Parameter Changes

The following table explains **why Q and R values were modified** and their **effect on system stability**.

| **Parameter**                 | **Old Value** | **New Value** | **Effect** |
|--------------------------------|--------------|--------------|------------|
| `Q[0,0]` (Cart Position)       | 1.0          | **50.0**     | Higher penalty on cart movement → **Prevents excessive displacement**. |
| `Q[1,1]` (Cart Velocity)       | 1.0          | **5.0**      | Smooths cart velocity → **Avoids erratic motion**. |
| `Q[2,2]` (Pole Angle)          | 10.0         | **100.0**    | Stronger correction for pole deviations → **Ensures better balance**. |
| `Q[3,3]` (Pole Angular Velocity) | 10.0      | **20.0**     | Dampens fast oscillations → **Prevents instability**. |
| `R` (Control Effort)           | 0.1          | **0.1**      | Increasing control penalty → **Reduces excessive force application**. |

### 🔹 **Final Outcome:**
✅ **Cart remains within ±2.5m range.**  
✅ **Pendulum stability improved (angle deviation ~22° max).**  
✅ **Control force application optimized (~70.12N max, efficiency 72%).** 

![working states and metrices](https://github.com/user-attachments/assets/98e5dc58-41b5-4f90-b453-ea1041c39dba)


3. Performance Analysis
   After applying the tuned LQR controller, system performance was analyzed using logged data from ROS2.

3.1 Duration of Stable Operation
   System remained stable for extended periods under disturbances.
   No unexpected cart ejections.
   Pole oscillations reduced significantly.
   
##  Maximum Cart Displacement

The following table compares **cart displacement before and after tuning**.

| **Test Condition**         | **Max Cart Displacement Observed** |
|---------------------------|-----------------------------------|
| **Initial LQR** (Q = [1,1,10,10], R=0.1)  | **~3.1m** (Exceeds limit) |
| **Tuned LQR** (Q = [20,5,100,20], R=0.5) | **~1.1m** (Within limits) |

🔹 **Final Outcome:**  
✅ **Final tuning ensures cart stays within the physical limit (±2.5m).**  

## 3.3 Maximum Pole Angle Deviation

The following table compares **pole stability before and after LQR tuning**.

| **Test Condition**       | **Max Pole Angle (θ)** |
|-------------------------|----------------------|
| **Initial LQR**         | ~1.75 rad (~100° tilt) |
| **Tuned LQR**           | ~0.4006 rad (~22° tilt) |

🔹 **Final Outcome:**  
✅ **Tuned LQR significantly improved pole stability, reducing excessive tilting.**  

## 3.4 Control Effort Analysis

The following table compares **control force intensity and efficiency**.

| **Metric**                | **Initial LQR** | **Tuned LQR** |
|---------------------------|----------------|---------------|
| **Peak Control Force**    | ~300N       | **70.12~N** |
| **Control Effort Efficiency** | **0%**  | **72%** |
| **Oscillations**          | High         | Dampened |

🔹 **Final Outcome:**  
✅ **The system is now more efficient with smoother force application.** 

![final metrices](https://github.com/user-attachments/assets/14d2a454-9b85-4dad-b045-95cede1dbbfc)

4. Experimental Observations
Key Improvements
Better cart position regulation → Kept within limits.
Less force-intensive control → Peak force reduced by 30%.
Pendulum stability improved → Lower angle deviation.
Reduced control effort oscillations.
Remaining Issues
Pole still oscillates (~22° tilt max) → Further fine-tuning needed.
Efficiency still not optimal (72%) → Can be increased with higher R values.

5. Recommendations for Further Improvements
1️⃣ Increase Q[2,2] = 120.0 to further stabilize the pole.
2️⃣ Increase R = 0.01 to improve control efficiency above 80%.
3️⃣ Try alternative control strategies (e.g., Reinforcement Learning).

## License
This work is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).
[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/) 
