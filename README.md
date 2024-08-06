# RasPatient Pi: A Low-cost Customizable LLM-based Virtual Standardized Patient Simulator

*RasPatient Pi* is a low-cost customizable LLM-based virtual standardized patient simulator. The simulator leverages automatic speech recognition, LLMs and text-to-speech engines. Scenarios can be specified by the teacher through a short description, while the clinical knowledge of LLMs is used to coherently complete any gap in the scenario.

The software is implemented as a [Django](https://www.djangoproject.com)-based web application. It uses OpenAI's API under the hood.

> The usage of OpenAI's API will generate costs. Users of *RasPatient Pi* are solely responsible for any generated cost and should closely monitor their usage!

## Installation

After cloning or downloading the code, install the dependencies using PIP:

```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

Create the database tables (we are using the default SQLite configuration, feel free to use any other database engine):

```bash
python manage.py makemigrations
python manage.py migrate
```

The software uses [MQTT](https://mqtt.org) for asynchronous message exchange and web sockets. Install a broker such as [Mosquitto](https://mosquitto.org):

```bash
sudo apt install mosquitto
```

Use the provided `mosquitto.conf` file to start the broker:

```bash
/usr/local/sbin/mosquitto -c mosquitto.conf
```

If Mosquitto is automatically started on your platform, create a link to the configuration:

```bash
sudo ln -s mosquitto.conf /etc/mosquitto/conf.d/mosquitto.conf
```

Make sure to allow port 9001 in your firewall:

```bash
sudo ufw allow 9001
```

## Configuration

Copy the template `config-dist.py` to create the configuration file:

```bash
cp config-dist.py config.py
```

Create a `DJANGO_SECRET_KEY` and fill in your `OPENAI_API_KEY`. Before the first run, create an [*Assistant*](https://platform.openai.com/docs/assistants/overview):

```bash
python manage.py createassistant
```

## Deployment

*RasPatient Pi* can be deployed on a single-board computer (such as a Raspberry Pi) to be used alongside a manikin or played in a browser, relying on a 3D avatar.

On our Raspberry Pi, we had to install a bunch of packages to get things running:

```bash
sudo apt install libcairo2-dev pkg-config python3-dev libgirepository1.0-dev portaudio19-dev python3-pyaudio firmware-sof-signed libgstreamer1.0-0 gstreamer1.0-dev gstreamer1.0-tools libx264-dev libjpeg-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-ugly gstreamer1.0-tools gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

To check configure the sound, use `alsamixer`.

Finally, to start *RasPatient Pi*, use:

```bash
python manage.py runserver
```

## Citation

```
@inproceedings{RasPatientPi2024,
    author={Grévisse, Christian},
	title={{RasPatient Pi: A Low-cost Customizable LLM-based Virtual Standardized Patient Simulator}},
	booktitle={Applied Informatics},
	year={2024},
}
```
