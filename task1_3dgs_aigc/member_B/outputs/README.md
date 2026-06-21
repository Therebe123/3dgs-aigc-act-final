# Member B Outputs

## Final 3DGS Scene

The final placement-checked Gaussian scene is compressed for GitHub size limits:

```bash
gzip -d -k task1_3dgs_aigc/member_B/outputs/renders/fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply.gz
```

Open `fused_scene_gaussian_clean_candidate_guitar_floor_v3.ply` in SuperSplat or another 3DGS viewer. The `counter.ply` background is preserved unchanged; `controller` and `bottle` keep the reviewed clean-candidate placement, while the guitar is moved down to the cabinet/floor side.

The final guitar adjustment is recorded by:

- `scripts/adjust_clean_candidate_guitar_floor_v3.py`
- `outputs/renders/guitar_floor_v3_stats.csv`
- `outputs/renders/guitar_floor_v3_topdown.png`

## Reproducibility Input

`fused_scene_gaussian_clean_candidate.ply.gz` is kept only as the reproducibility input for the final guitar adjustment script. It is not the recommended file to submit or inspect.
