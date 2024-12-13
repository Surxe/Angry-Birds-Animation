import maya.cmds as mc
import math  # Import math module for sin, cos functions

def apply_parabolic_motion():
    # Prompt user for initial velocity and angle
    velocity = mc.promptDialog(
        title='Initial Velocity', 
        message='Enter initial velocity (m/s):', 
        button=['OK', 'Cancel'], 
        defaultButton='OK', 
        cancelButton='Cancel', 
        dismissString='Cancel')

    if velocity == 'OK':
        velocity = float(mc.promptDialog(query=True, text=True))
    else:
        return  # Exit if the user cancels the prompt

    angle = mc.promptDialog(
        title='Angle', 
        message='Enter angle (degrees):', 
        button=['OK', 'Cancel'], 
        defaultButton='OK', 
        cancelButton='Cancel', 
        dismissString='Cancel')

    if angle == 'OK':
        angle = float(mc.promptDialog(query=True, text=True))
    else:
        return  # Exit if the user cancels the prompt

    gravity = 9.8  # Gravity constant in m/s^2 

    # Ensure exactly one object is selected
    selected_objects = mc.ls(sl=True)
    if not selected_objects:
        raise RuntimeError("No object selected. Please select an object before running the script.")
    elif len(selected_objects) > 1:
        raise RuntimeError("Multiple objects selected. Please select a single object.")

    var1 = selected_objects[0]

    # Ensure the selected object is a transform node
    if not mc.objectType(var1) == "transform":
        raise RuntimeError(f"The selected object '{var1}' is not a transform node.")
        
    # Convert angle to radians
    angle_rad = math.radians(angle)

    # Calculate velocity components
    velY = velocity * math.sin(angle_rad)  # Vertical velocity component
    velX = velocity * math.cos(angle_rad)  # Horizontal velocity component

    # Add toggle and start position attributes if they don't exist
    if not mc.objExists(f"{var1}.applyParabolic"):
        mc.addAttr(var1, longName="applyParabolic", attributeType="bool", defaultValue=False)
        mc.setAttr(f"{var1}.applyParabolic", keyable=True)

    if not mc.objExists(f"{var1}.startPosX"):
        mc.addAttr(var1, longName="startPosX", attributeType="double", defaultValue=0.0)
        mc.setAttr(f"{var1}.startPosX", keyable=False)

    if not mc.objExists(f"{var1}.startPosY"):
        mc.addAttr(var1, longName="startPosY", attributeType="double", defaultValue=0.0)
        mc.setAttr(f"{var1}.startPosY", keyable=False)

    if not mc.objExists(f"{var1}.startTime"):
        mc.addAttr(var1, longName="startTime", attributeType="double", defaultValue=0.0)
        mc.setAttr(f"{var1}.startTime", keyable=False)

    # Generate a unique expression name
    expression_name = f"{var1}_parabolicMotion"
    if mc.objExists(expression_name):
        mc.delete(expression_name)  # Delete any existing expression with the same name

    # Create the MEL-style expression
    expression = f"""
    if (`getAttr {var1}.applyParabolic` == 1) // Check if the toggle is on
    {{
        // Record start time and positions once
        if (`getAttr {var1}.startTime` == 0) // Only set startTime when motion starts
        {{
            {var1}.startPosX = {var1}.translateX;
            {var1}.startPosY = {var1}.translateY;
            {var1}.startTime = time; // Store the time when the toggle was activated
        }}

        float $startX = {var1}.startPosX;
        float $startY = {var1}.startPosY;
        float $startTime = {var1}.startTime;

        float $elapsedTime = time - $startTime; // Calculate elapsed time since motion began

        float $posY = $startY + ({velY} * $elapsedTime - 0.5 * {gravity} * $elapsedTime * $elapsedTime); // Vertical motion
        float $posX = $startX + {velX} * $elapsedTime; // Horizontal motion

        if ($posY > 0) {{
            {var1}.translateY = $posY;  // Ensure the object stays above ground (no negative Y position)
            {var1}.translateX = $posX;  // Horizontal motion of the object
        }} else {{
            {var1}.translateY = 0;  // Stop at ground level
        }}
    }}
    else
    {{
        // Reset start positions and time when the toggle is off
        {var1}.startPosX = 0;
        {var1}.startPosY = 0;
        {var1}.startTime = 0;
    }}
    """

    # Apply the expression
    mc.expression(s=expression, name=expression_name)
    print(f"Parabolic motion expression applied to {var1} with velocity={velocity} m/s and angle={angle} degrees.")

# Call the function
apply_parabolic_motion()
