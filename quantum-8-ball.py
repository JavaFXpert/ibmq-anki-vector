#!/usr/bin/env python3

"""Go to pose

Make Vector go to a pose.
"""

import anki_vector
import os
import sys
import time

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
        # robot.screen.set_screen_with_image_data(screen_data, 4.0)
        # time.sleep(5)

    image2screen("qiskit-logo.png")

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
        print('The Quantum 8-ball says:')
        robot.say_text("The Quantum 8-ball says, ")
        if state == '000':
            image2screen("ket-000.png")
            print('It is certain.')
            robot.say_text("It is certain.")
        elif state == '001':
            image2screen("ket-001.png")
            print('Without a doubt.')
            robot.say_text("Without a doubt.")
        elif state == '010':
            image2screen("ket-010.png")
            print('Yes - definitely.')
            robot.say_text("Yes - definitely.")
        elif state == '011':
            image2screen("ket-011.png")
            print('Most likely.')
            robot.say_text("Most likely.")
        elif state == '100':
            image2screen("ket-100.png")
            print("Don't count on it.")
            robot.say_text("Don't count on it.")
        elif state == '101':
            image2screen("ket-101.png")
            print('My reply is no.')
            robot.say_text("My reply is no.")
        elif state == '110':
            image2screen("ket-110.png")
            print('Very doubtful.')
            robot.say_text("Very doubtful.")
        else:
            image2screen("ket-111.png")
            print('Concentrate and ask again.')
            robot.say_text("Concentrate and ask again.")

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

    # see a list of available remote backends
    ibmq_backends = IBMQ.backends()

    print("Remote backends: ", ibmq_backends)
    # Compile and run the Quantum Program on a real device backend
    try:
        least_busy_device = least_busy(IBMQ.backends(simulator=False))
        print("Running on current least busy device: ", least_busy_device)

        if least_busy_device == "ibmx4":
            device_name = "IBM 5 qubit quantum computer in New York"
        elif least_busy_device == "ibmq_16_melbourne":
            device_name = "IBM 16 qubit quantum computer in Melbourne, Australia"

        robot.say_text("Hold on. I'm going to ask an ", device_name, "to run the quentum program")
        #running the job
        job_exp = execute(qc, least_busy_device, shots=1024, max_credits=10)
        result_exp = job_exp.result()

        # Show the results
        print("experiment: ", result_exp)
        print(result_exp.get_counts(qc))
    except:
        print("All devices are currently unavailable.")

    # If necessary, move Vector's Head and Lift to make it easy to see his face
    robot.behavior.set_head_angle(degrees(45.0))
    robot.behavior.set_lift_height(0.0)

    # Disconnect from Vector
    robot.disconnect()

if __name__ == "__main__":
    main()
