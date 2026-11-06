## Outcome

premise_failed

## Surprises / judgment calls

The drain premise park can be reused, but the serve scheduler receives only parsed tickets and journal state; neither contains the current committed ticket blob SHA.

## Dead ends

Deriving the repository from the journal directory would fail for configured state directories and would bypass the git seam.

## Second problems filed

none

## Resolved engine/model

- provider: codex
- model: gpt-6.1-terra
- spec: implement 2.2

## Predicted vs actual

The ticket allowed 75 minutes expected and 90 minutes stuck; investigation stopped after identifying the scope conflict.

