#!/usr/bin/env python3

"""Go to pose

Make Vector go to a pose.
"""

import anki_vector
import os
import sys
import time
from anki_vector.behavior import MIN_HEAD_ANGLE, MAX_HEAD_ANGLE
from anki_vector.util import Angle


try:
    from PIL import Image
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install --user Pillow` to install")

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, IBMQ, Aer
from qiskit.backends.ibmq import least_busy


def main():
    args = anki_vector.util.parse_command_args()
    from anki_vector.util import degrees, Pose

    # Create a Robot object
    robot = anki_vector.Robot()

    # Connect to the Robot
    robot.connect()

    def image2screen(image_file_name):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(current_directory, "images", image_file_name)

        # Load an image
        image_file = Image.open(image_path)

        # Convert the image to the format used by the Screen
        print("Display image on Vector's face...")
        screen_data = anki_vector.screen.convert_image_to_screen_data(image_file)
        robot.conn.release_control()
        time.sleep(1)
        robot.conn.request_control()
        robot.screen.set_screen_with_image_data(screen_data, 10.0, interrupt_running=True)
        robot.behavior.set_head_angle(MAX_HEAD_ANGLE)
        time.sleep(3)
        robot.behavior.set_head_angle(Angle(0.0))

    robot.world.disconnect_cube()
    robot.behavior.drive_off_charger()

    robot.say_text("I wonder if I will find my true love today?")

    print("Connecting to a cube...")
    robot.world.connect_cube()

    robot.say_text("I got it! I'll ask a quantum eight ball on an IBM quantum computer.")
    image2screen("qiskit-logo.png")

    if robot.world.connected_light_cube:
        print("Begin cube docking...")
        dock_response = robot.behavior.dock_with_cube(
            robot.world.connected_light_cube,
            num_retries=4)
        if dock_response:
            docking_result = dock_response.result

        if docking_result:
            if docking_result.code != anki_vector.messaging.protocol.ActionResult.ACTION_RESULT_SUCCESS:
                print("Cube docking failed with code {0} ({1})".format(str(docking_result).rstrip('\n\r'),
                                                                       docking_result.code))
        else:
            print("Cube docking failed.")

        robot.world.disconnect_cube()

    # Authenticate for access to remote backends
    try:
        IBMQ.load_accounts()
    except:
        print("""WARNING: There's no connection with the API for remote backends.
                 Have you initialized a file with your personal token?
                 For now, there's only access to local simulator backends...""")

    # Set up quantum register and classical register for 1 qubit
    q = QuantumRegister(1)
    c = ClassicalRegister(1)

    # Create a quantum circuit
    qc = QuantumCircuit(q, c)
    qc.h(q)
    qc.measure(q, c)

    def answer(result):
        for key in result.keys():
            state = key

        print('The Quantum 8-ball says:')
        robot.say_text("The Quantum 8-ball says, ")
        if state == '1':
            image2screen("ket-1.png")
            print('Yes - definitely.')
            robot.say_text("Yes - definitely.")
            robot.anim.play_animation('anim_eyepose_happy')
            robot.anim.play_animation('anim_eyecontact_giggle_01_head_angle_20')
            robot.anim.play_animation('anim_reacttocliff_edge_01')
            robot.say_text('Fist bump!')
            robot.anim.play_animation('anim_fistbump_requestoncelong_01')
            robot.say_text('Later! Gotta go find my true love!')
            robot.behavior.set_lift_height(0.0)

            robot.behavior.drive_on_charger()

        elif state == '0':
            image2screen("ket-0.png")
            print('My reply is no.')
            robot.say_text("My reply is no.")
            robot.behavior.set_head_angle(MIN_HEAD_ANGLE)
            robot.anim.play_animation('anim_eyepose_sad_down')
            robot.say_text("I guess I should just go back home")
            robot.behavior.drive_on_charger()

    # Run the circuit on an IBM quantum simulator
    # Note: To run circuits on an IBM quantum computer, see instructions
    #       in the Jupyter notebook of the following Qiskit tutorial:
    # https://github.com/Qiskit/qiskit-tutorials/blob/master/qiskit/basics/getting_started_with_qiskit_terra.ipynb
    job = execute(qc, backend=Aer.get_backend('qasm_simulator'), shots=1)
    result = job.result().get_counts(qc)
    answer(result)

    # Show the results
    print("result: ", result)

    # Disconnect from Vector
    robot.disconnect()

if __name__ == "__main__":
    main()
