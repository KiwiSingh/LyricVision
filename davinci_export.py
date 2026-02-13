from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom
import os
import urllib.parse


def seconds_to_fcp_time(seconds, fps):
    frames = int(round(seconds * fps))
    return f"{frames}/{fps}s"


def export_fcpxml(
    videos,
    timeline,
    resolution="1080p",
    fps=24,
    output_path="LyricVision_Output.fcpxml"
):

    if not timeline:
        raise ValueError("Timeline empty.")

    if not videos:
        raise ValueError("Videos empty.")

    # Resolution
    if resolution == "4K":
        width, height = 3840, 2160
    else:
        width, height = 1920, 1080

    fcpxml = Element("fcpxml", version="1.9")
    resources = SubElement(fcpxml, "resources")

    format_id = "r1"
    SubElement(resources, "format", {
        "id": format_id,
        "frameDuration": f"1/{fps}s",
        "width": str(width),
        "height": str(height)
    })

    asset_ids = []

    # =====================================================
    # CREATE ASSETS (STRICT LOCAL FILE REQUIREMENT)
    # =====================================================

    for i, video in enumerate(videos):

        local_path = video.get("local_path")

        if not local_path or not os.path.exists(local_path):
            raise ValueError(f"Missing local file for video: {video}")

        asset_id = f"a{i+1}"
        asset_ids.append(asset_id)

        duration_seconds = float(video.get("duration", 5))
        duration_tc = seconds_to_fcp_time(duration_seconds, fps)

        abs_path = os.path.abspath(local_path)
        encoded_path = urllib.parse.quote(abs_path)
        file_url = f"file://{encoded_path}"

        asset = SubElement(resources, "asset", {
            "id": asset_id,
            "name": os.path.basename(local_path),
            "start": "0s",
            "duration": duration_tc,
            "hasVideo": "1",
            "format": format_id
        })

        SubElement(asset, "media-rep", {
            "kind": "original-media",
            "src": file_url
        })

    # =====================================================
    # BUILD SEQUENCE
    # =====================================================

    library = SubElement(fcpxml, "library")
    event = SubElement(library, "event", {"name": "LyricVision"})
    project = SubElement(event, "project", {"name": "Lyric Timeline"})

    total_duration = sum(
        max(1.0 / fps, clip["duration"])
        for clip in timeline
    )

    total_tc = seconds_to_fcp_time(total_duration, fps)

    sequence = SubElement(project, "sequence", {
        "format": format_id,
        "duration": total_tc,
        "tcStart": "0s",
        "tcFormat": "NDF"
    })

    spine = SubElement(sequence, "spine")

    current_offset = 0.0

    for i, clip in enumerate(timeline):

        asset_id = asset_ids[i % len(asset_ids)]

        duration_seconds = max(1.0 / fps, clip["duration"])
        duration_tc = seconds_to_fcp_time(duration_seconds, fps)
        offset_tc = seconds_to_fcp_time(current_offset, fps)

        SubElement(spine, "asset-clip", {
            "name": clip.get("text", ""),
            "ref": asset_id,
            "offset": offset_tc,
            "start": "0s",
            "duration": duration_tc
        })

        current_offset += duration_seconds

    xml_str = tostring(fcpxml)
    pretty = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_path, "w") as f:
        f.write(pretty)