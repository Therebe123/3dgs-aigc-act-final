# Member B Outputs

Large Gaussian fusion output is compressed for GitHub size limits:

```bash
gzip -d -k task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian.ply.gz
```

Then open `fused_scene_gaussian.ply` with a 3DGS-compatible viewer such as Nerfstudio/SIBR/gsplat. Blender preview artifacts are included only for quick visual inspection.

Current `fused_scene_gaussian.ply.gz` preserves the native `counter.ply` kitchen background bounds and uses interpolated OBJ vertex colors for object B/C, so it should not appear as the old normalized background or pure-color silhouettes.

## Final Clean Candidate

The final placement-checked Gaussian scene is:

```bash
gzip -d -k task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz
```

Open `fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply` in SuperSplat or another 3DGS viewer. The `counter.ply` background is preserved unchanged; `controller` and `bottle` keep the reviewed clean-candidate placement, while the guitar is moved down to the cabinet/floor side. The original transform table is in `docs/transforms_clean_candidate.csv`; the final guitar adjustment is recorded by `scripts/adjust_clean_candidate_guitar_floor_v3.py`, `outputs/renders/guitar_floor_v3_stats.csv`, and `outputs/renders/guitar_floor_v3_topdown.png`.
