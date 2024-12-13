import maya.cmds as mc
import math  # Import math module for sin, cos functions

def apply_parabolic_motion():
    # Prompt user for initial velocity, angle, scaler, and starting frame
    velocity = mc.promptDialog(
        title='Initial Velocity',
        message='Enter initial velocity (m/s):',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    if velocity == 'OK':
        velocity = float(mc.promptDialog(query=True, text=True))
    else:
        return

    angle = mc.promptDialog(
        title='Angle',
        message='Enter angle (degrees):',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    if angle == 'OK':
        angle = float(mc.promptDialog(query=True, text=True))
    else:
        return

    scaler = mc.promptDialog(
        title='Time Scaler',
        message='Enter a scaler:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    if scaler == 'OK':
        scaler = float(mc.promptDialog(query=True, text=True))
    else:
        return

    startFrame = mc.promptDialog(
        title='Starting Frame',
        message='Enter a frame number:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )
    if startFrame == 'OK':
        startFrame = float(mc.promptDialog(query=True, text=True))
    else:
        return

    gravity = 9.8  # Gravity constant in m/s^2

    # Ensure exactly one object is selected
    selected_objects = mc.ls(sl=True)
    if not selected_objects:
        raise RuntimeError("No object selected. Please select an object before running the script.")
    elif len(selected_objects) > 1:
        raise RuntimeError("Multiple objects selected. Please select a single object.")

    var1 = selected_objects[0]

    # Ensure the selected object is a transform node
    if mc.objectType(var1) != "transform":
        raise RuntimeError(f"The selected object '{var1}' is not a transform node.")

    # Convert angle to radians
    angle_rad = math.radians(angle)

    # Calculate velocity components
    velY = velocity * math.sin(angle_rad)
    velZ = velocity * math.cos(angle_rad)

    # Add custom attributes if they don't exist
    if not mc.objExists(f"{var1}.startPosZ"):
        mc.addAttr(var1, longName="startPosZ", attributeType="double", defaultValue=0.0)
        mc.setAttr(f"{var1}.startPosZ", keyable=False)

    if not mc.objExists(f"{var1}.startPosY"):
        mc.addAttr(var1, longName="startPosY", attributeType="double", defaultValue=0.0)
        mc.setAttr(f"{var1}.startPosY", keyable=False)

    if not mc.objExists(f"{var1}.startTime"):
        mc.addAttr(var1, longName="startTime", attributeType="double", defaultValue=0.0)
        mc.setAttr(f"{var1}.startTime", keyable=False)

    # Generate a unique expression name
    expression_name = f"{var1}_parabolicMotion"
    if mc.objExists(expression_name):
        mc.delete(expression_name)

    # Create the MEL-style expression
    expression = f"""
    if (frame >= {startFrame}) {{
        if (`getAttr {var1}.startTime` == 0) {{
            {var1}.startPosZ = {var1}.translateZ;
            {var1}.startPosY = {var1}.translateY;
            {var1}.startTime = time; // Store the time when the toggle was activated
        }}

        float $startZ = {var1}.startPosZ;
        float $startY = {var1}.startPosY;
        float $startTime = {var1}.startTime;

        float $elapsedTime = (time - $startTime) * {scaler};
        float $posY = $startY + ({velY} * $elapsedTime - 0.5 * {gravity} * $elapsedTime * $elapsedTime);
        float $posZ = $startZ + {velZ} * $elapsedTime;

        if ($posY > -600) {{
            {var1}.translateY = $posY;
            {var1}.translateZ = $posZ;
        }}
    }}
    
    if(frame == 1)
    {{
            {var1}.translateY = 0;
            {var1}.translateZ = 0;
            {var1}.translateX = 0;
    }} 
    """

    # Apply the expression
    mc.expression(s=expression, name=expression_name)
    print(f"Parabolic motion applied to {var1} with velocity={velocity} m/s and angle={angle} degrees.")

apply_parabolic_motion()
