# AutoMatLinker 

**AutoMatLinker** is a Maya Python tool that automatically assigns shaders and links textures to selected meshes based on naming conventions.  

---

### Features

- Automatically detects selected meshes and applies a `standardSurface` shader.
- Links base color textures based on object name (e.g. `_albedo`, `_normal`, `_roughness`)
- Supports shared textures using the `"shared_"` prefix (e.g., `shared_chess_pieces_baseColor.png`)
- Smart name-stripping (e.g. removes `_01`) to increase texture match accuracy
- Fallback and warning system when textures aren’t found

---

### Naming Conventions

| **Type**         | **Example Mesh Name**       | **Expected Texture Name(s)**                        |
|------------------|------------------------------|-----------------------------------------------------|
| Unique Texture   | `white_chess_rook`           | `white_chess_rook_albedo.png`                   |
| Unique Texture   | `white_chess_rook_02`        | `white_chess_rook_normal.png`                      |
| Shared Texture   | `black_chess_rook_01`        | `shared_black_chess_pieces_albedo.png`          |
| Shared Texture   | `white_chess_bishop_03`      | `shared_white_chess_pieces_specular.png`           |

---

### ⚙️ Installation & Setup

#### Requirements

- **Autodesk Maya**: 2020 or later (tested on 2024)
- **Python**: Maya’s built-in Python (3.x recommended)

---

#### Setup Instructions

1. **Clone or download** this repository and save it to your Maya scripts folder:

    ```
    C:\Users\<YourUsername>\Documents\maya\<YourMayaVersion>\scripts
    ```

2. **Launch Maya**, open the **Script Editor**, and switch to the **Python** tab.

3. Run the following MEL command in the **MEL tab** of the **Script Editor**:

    ```
    commandPort -name "localhost:7001" -sourceType "mel" -echoOutput;
    ```

4. **Import and run the tool** 
