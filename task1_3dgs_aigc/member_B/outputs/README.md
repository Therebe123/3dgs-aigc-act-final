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
gzip -d -k task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate.ply.gz
```

Open `fused_scene_gaussian_clean_candidate.ply` in SuperSplat or another 3DGS viewer. The `counter.ply` background is preserved unchanged; `controller`, `bottle`, and `guitar` were transformed independently before the final merge. The transform table is in `docs/transforms_clean_candidate.csv`, and the top-down placement check is `outputs/renders/fused_scene_gaussian_clean_candidate_topdown_check.png`.

