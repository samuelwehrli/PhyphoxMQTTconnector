#!/usr/bin/env python3
"""Measure the actual MQTT message rate coming from a phyphox experiment.

Subscribes to the given topic, timestamps every message on arrival, and
reports the achieved frequency plus inter-arrival jitter once the duration
elapses (or Ctrl+C is pressed).

Usage:
    python tools/measure_rate.py --topic zhaw/pcls/phyphox/krft
    python tools/measure_rate.py --topic zhaw/pcls/phyphox/krft --duration 20
"""
import argparse
import json
import statistics
import time

import paho.mqtt.client as mqtt

arrival_times = []
first_payload = None


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected (reason_code={reason_code}), subscribing to '{userdata['topic']}'...")
    client.subscribe(userdata["topic"])


def on_message(client, userdata, msg):
    global first_payload
    now = time.monotonic()
    arrival_times.append(now)
    if first_payload is None:
        try:
            first_payload = json.loads(msg.payload)
        except (json.JSONDecodeError, ValueError):
            first_payload = msg.payload
    if userdata["verbose"]:
        print(f"[{len(arrival_times):4d}] {now:.3f}  {msg.payload[:120]!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="test.mosquitto.org")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", required=True, help="e.g. zhaw/pcls/phyphox/krft")
    parser.add_argument("--duration", type=float, default=15.0, help="seconds to listen (default: 15)")
    parser.add_argument("--verbose", action="store_true", help="print every message as it arrives")
    args = parser.parse_args()

    userdata = {"topic": args.topic, "verbose": args.verbose}
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()

    print(f"Listening for {args.duration:.0f}s on {args.host}:{args.port} ...")
    try:
        time.sleep(args.duration)
    except KeyboardInterrupt:
        pass
    client.loop_stop()
    client.disconnect()

    if len(arrival_times) < 2:
        print(f"\nOnly received {len(arrival_times)} message(s) — not enough to measure a rate.")
        print("Check that the phone is actively sending and the topic matches exactly.")
        return

    span = arrival_times[-1] - arrival_times[0]
    intervals = [b - a for a, b in zip(arrival_times, arrival_times[1:])]
    mean_interval = statistics.mean(intervals)
    achieved_hz = (len(arrival_times) - 1) / span

    print("\n--- Results ---")
    print(f"Messages received:     {len(arrival_times)}")
    print(f"Observation window:    {span:.3f}s")
    print(f"Achieved rate:         {achieved_hz:.2f} Hz  (target interval = {mean_interval*1000:.1f} ms)")
    print(f"Mean interval:         {mean_interval*1000:.1f} ms")
    print(f"Median interval:       {statistics.median(intervals)*1000:.1f} ms")
    if len(intervals) > 1:
        print(f"Jitter (stdev):        {statistics.stdev(intervals)*1000:.1f} ms")
    print(f"Min / Max interval:    {min(intervals)*1000:.1f} ms / {max(intervals)*1000:.1f} ms")

    if isinstance(first_payload, dict):
        print(f"\nExample payload keys:  {list(first_payload.keys())}")


if __name__ == "__main__":
    main()
