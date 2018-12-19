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

    # def event_listener(name, msg):
    #     print(name)  # will print 'my_event'
    #     print(msg)  # will print 'my_event dispatched'

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
        # robot.screen.set_screen_with_image_data(screen_data, 4.0)
        time.sleep(3)
        robot.behavior.set_head_angle(Angle(0.0))

    print("List all animation names:")
    anim_names = robot.anim.anim_list
    for anim_name in anim_names:
        print(anim_name)

    robot.world.disconnect_cube()
    robot.behavior.drive_off_charger()

    robot.say_text("I wonder if I will find my true love today?")

    print("Connecting to a cube...")
    robot.world.connect_cube()

    if robot.world.connected_light_cube:
        robot.say_text("I got it! I'll ask a quantum eight ball on an IBM quantum computer.")
        image2screen("qiskit-logo.png")
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

    # robot.anim.play_animation('anim_feedback_iloveyou_02')
    # robot.anim.play_animation('anim_dancebeat_scoot_right_01')

    # Authenticate for access to remote backends
    try:
        IBMQ.load_accounts()
    except:
        print("""WARNING: There's no connection with the API for remote backends.
                 Have you initialized a file with your personal token?
                 For now, there's only access to local simulator backends...""")

    # set up Quantum Register and Classical Register for 3 qubits
    q = QuantumRegister(3)
    c = ClassicalRegister(3)
    # Create a Quantum Circuit
    qc = QuantumCircuit(q, c)
    qc.h(q)
    qc.measure(q, c)

    def answer(result):
        for key in result.keys():
            state = key
        # TODO: Remove next line
        state = '010'

        print('The Quantum 8-ball says:')
        robot.say_text("The Quantum 8-ball says, ")
        if state == '000':
            image2screen("ket-000.png")
            print('It is certain.')
            robot.say_text("It is certain.")
            robot.anim.play_animation('anim_petting_bliss_getout_01')

        elif state == '001':
            image2screen("ket-001.png")
            print('Without a doubt.')
            robot.say_text("Without a doubt.")
            robot.anim.play_animation('anim_petting_bliss_getout_01')

        elif state == '010':
            image2screen("ket-010.png")
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

        elif state == '011':
            image2screen("ket-011.png")
            print('Most likely.')
            robot.say_text("Most likely.")
            robot.anim.play_animation('anim_petting_bliss_getout_01')

        elif state == '100':
            image2screen("ket-100.png")
            print("Don't count on it.")
            robot.say_text("Don't count on it.")
            robot.anim.play_animation('anim_petting_bliss_getout_01')

        elif state == '101':
            image2screen("ket-101.png")
            print('My reply is no.')
            robot.say_text("My reply is no.")
            robot.anim.play_animation('anim_petting_bliss_getout_01')

        elif state == '110':
            image2screen("ket-110.png")
            print('Very doubtful.')
            robot.say_text("Very doubtful.")
            robot.behavior.set_head_angle(MIN_HEAD_ANGLE)
            robot.anim.play_animation('anim_eyepose_sad_down')
            robot.say_text("I guess I should just go back home")
            robot.behavior.drive_on_charger()

        else:
            image2screen("ket-111.png")
            print('Concentrate and ask again.')
            robot.say_text("Concentrate and ask again.")
            robot.anim.play_animation('anim_petting_bliss_getout_01')

    job = execute(qc, backend=Aer.get_backend('qasm_simulator'), shots=1)
    result = job.result().get_counts(qc)
    answer(result)

    # See a list of available local simulators
    print("Aer backends: ", Aer.backends())
    backend_sim = Aer.get_backend('qasm_simulator')

    # Compile and run the Quantum circuit on a simulator backend
    job_sim = execute(qc, backend_sim)
    result_sim = job_sim.result()

    # Show the results
    print("simulation: ", result_sim)
    print(result_sim.get_counts(qc))

    # # see a list of available remote backends
    # ibmq_backends = IBMQ.backends()
    #
    # print("Remote backends: ", ibmq_backends)
    # # Compile and run the Quantum Program on a real device backend
    # try:
    #     least_busy_device = least_busy(IBMQ.backends(simulator=False))
    #     print("Running on current least busy device: ", least_busy_device)
    #
    #     if least_busy_device == "ibmx4":
    #         device_name = "IBM 5 qubit quantum computer in New York"
    #     elif least_busy_device == "ibmq_16_melbourne":
    #         device_name = "IBM 16 qubit quantum computer in Melbourne, Australia"
    #
    #     robot.say_text("Hold on. I'm going to ask an ", device_name, "to run the quentum program")
    #     #running the job
    #     job_exp = execute(qc, least_busy_device, shots=1024, max_credits=10)
    #     result_exp = job_exp.result()
    #
    #     # Show the results
    #     print("experiment: ", result_exp)
    #     print(result_exp.get_counts(qc))
    # except:
    #     print("All devices are currently unavailable.")

    # If necessary, move Vector's Head and Lift to make it easy to see his face
    # robot.behavior.set_head_angle(degrees(45.0))
    # robot.behavior.set_lift_height(0.0)

    # Disconnect from Vector
    robot.disconnect()

if __name__ == "__main__":
    main()
