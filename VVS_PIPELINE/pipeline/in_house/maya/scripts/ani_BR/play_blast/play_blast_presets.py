

class PlayblastCustomPresets(object):


    RESOLUTION_PRESETS = [
        #
        # Format:  ["preset_name", (width, height)],
        #
        ["HD 2048", (2048, 1152)],
        ["HD 1080", (1920, 1080)],
        ["HD 720", (1280, 720)],
        ["HD 540", (960, 540)],
    ]


    VIEWPORT_VISIBILITY_PRESETS = [
        #
        # Format: ["preset_name", ["type_name_1", "type_name_2", ...]],
        #
        # Viewport visibility types:
        #
        #    Controllers            NURBS Curves      NURBS Surfaces          NURBS CVs
        #    NURBS Hulls            Polygons          Subdiv Surfaces         Planes
        #    Lights                 Cameras           Image Planes            Joints
        #    IK Handles             Deformers         Dynamics                Particle Instancers
        #    Fluids                 Hair Systems      Follicles               nCloths
        #    nParticles             nRigids           Dynamic Constraints     Locators
        #    Dimensions             Pivots            Handles                 Texture Placements
        #    Strokes                Motion Trails     Plugin Shapes           Clip Ghosts
        #    Grease Pencil          Grid              HUD                     Hold-Outs
        #    Selection Highlighting
        #

        ["Geo", ["NURBS Surfaces", "Polygons"]],
        ["Dynamics", ["NURBS Surfaces", "Polygons", "Dynamics", "Fluids", "nParticles"]],
    ]

    PLAYBLAST_OUTPUT_PATH_LOOKUP = [
        #
        # Format:  ("display_name", "{tag_name}"),
        #
    ]

    PLAYBLAST_OUTPUT_FILENAME_LOOKUP = [
        #
        # Format:  ("display_name", "{tag_name}"),
        #
    ]


    @classmethod
    def parse_playblast_output_dir_path(self, dir_path):
        """
        User defined output directory {tags}. Logic should replace tag with a string.

        PLAYBLAST_OUTPUT_PATH_LOOKUP can be used to add {tag} to context menu.
        """
        # if "{my_tag}" in dir_path:
        #     dir_path = dir_path.replace("{my_tag}", "My Custom Value")

        return dir_path

    @classmethod
    def parse_playblast_output_filename(self, filename):
        """
        User defined output filenname {tags}. Logic should replace tag with a string.

        PLAYBLAST_OUTPUT_FILENAME_LOOKUP can be used to add {tag} to context menu.
        """
        # if "{my_tag}" in filename:
        #     filename = filename.replace("{my_tag}", "My Custom Value")

        return filename


class PlayBlastCustomPresets(object):


    SHOT_MASK_LABEL_LOOKUP = [
        #
        # Format:  ("display_name", "{tag_name}"),
        #
    ]

    @classmethod
    def parse_shot_mask_text(self, text):
        """
        User defined shot mask label {tags}. Logic should replace tag with a string.

        SHOT_MASK_LABEL_LOOKUP can be used to add {tag} to context menu.
        """
        # if "{my_tag}" in text:
        #     text = text.replace("{my_tag}", "My Custom Value")

        return text

