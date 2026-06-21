# Object C Final Deliverables

Object C uses the user-provided segmented guitar image and Stable-Zero123.

| Item | Content / Path |
|---|---|
| Original input image | `homework/member_B/assets/object_C/input.png` |
| User-segmented image | `homework/member_B/assets/object_C/image.png` |
| Transparent input used for training | `homework/member_B/assets/object_C/input_rgba.png` |
| Model | `stabilityai/stable-zero123`, local checkpoint `homework/member_B/repos/threestudio/load/zero123/stable_zero123.ckpt` |
| Config | `homework/member_B/repos/threestudio/configs/stable-zero123.yaml` |
| Training steps | `600` |
| Training log | `homework/member_B/logs/object_C_zero123_train.log` |
| Preview image | `homework/member_B/assets/object_C/object_C_preview.png` |
| Training grid | `homework/member_B/assets/object_C/object_C_training_grid.png` |
| Turntable video | `homework/member_B/assets/object_C/object_C_turntable.mp4` |
| Final validation video | `homework/member_B/assets/object_C/object_C_final_val.mp4` |
| Mesh | `homework/member_B/assets/object_C/object_C.obj` |
| Final checkpoint | `homework/member_B/results/object_C_zero123/object_C_guitar_stable_zero123/[64, 128, 256]_input_rgba.png@20260621-171641/ckpts/epoch=0-step=600.ckpt` |
| Full output directory | `homework/member_B/results/object_C_zero123/object_C_guitar_stable_zero123/[64, 128, 256]_input_rgba.png@20260621-171641` |

Notes: `image.png` is the manually cleaned guitar image supplied by the user. It was converted to true RGBA alpha and saved as `input_rgba.png`; this transparent PNG is the actual `data.image_path` used by Stable-Zero123. The current Object C deliverable covers the homework row requiring input image, background-removed image, generation model, result image, and log. Mesh export has also been completed and saved as `object_C.obj` for the final fusion scene.
