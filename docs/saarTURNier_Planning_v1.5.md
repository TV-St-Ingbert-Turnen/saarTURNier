# saarTURNier System – Planning & Design Document (v1.5)

## Purpose

This document defines the **final, agreed planning baseline** for the saarTURNier System.
It captures domain rules, state models, workflows, roles, and aggregation logic with
sufficient precision for implementation by downstream agents.

This document is **planning-only**.  
No implementation details, frameworks, or code are prescribed beyond architectural intent.

---

## 1. Scope & Core Assumptions

- Exactly **one active competition** at a time
- Archived competitions are **read-only via UI**
- Corrections to archived data require **direct database changes**
- No score versioning is required
- The system is **domain-specific**, not a generic scoring framework

---

## 2. Roles & Permissions

### 2.1 Visitors / Athletes
- No login
- Read-only access
- See:
  - published scores
  - rankings
  - schedules
- Athletes and visitors are the same role

### 2.2 Judges Panels
- One login **per judges panel** (no individual judge identities)
- One tablet per judges panel
- For each **apparatus pair**, there exist **two judges panels**:
  - one for women
  - one for men

#### Fairness & Assignment Invariant (Critical)

- A **judges panel may score multiple apparatus** during a competition.
- However, **each apparatus (gender-specific) must be scored by exactly one judges panel throughout the entire competition**.
- Once a judges panel is assigned to score an apparatus, **no other judges panel may score that apparatus** in any rotation.
- This invariant ensures score comparability and fairness across rotation groups and rotations.

- Male and female judges panels:
  - score independently according to their respective rules
  - may be assigned to more than one apparatus (subject to the invariant above)
  - must never score more than one apparatus **within the same rotation**

- Judges panels may:
  - enter scores for their gender
  - edit scores for their gender
  - mark **their side** of an apparatus pair as completed
- Judges panels are strictly constrained by rotation and apparatus state

### 2.3 Organizers
- Full control role
- May:
  - edit scores **at any time**, regardless of rotation or apparatus state
  - reopen a **judges panel side** within an ACTIVE rotation
  - end rotations explicitly
  - publish results implicitly by ending a rotation
  - close competitions
- Organizer score edits **never change rotation state**

---

## 3. Competition Structure

### 3.1 Apparatus Pairs (Fixed)

1. Floor (Men & Women)
2. Vault (Men & Women)
3. Bars  
   - Women: Uneven Bars  
   - Men: Horizontal Bar
4. Beam / Parallel Bars  
   - Women: Balance Beam  
   - Men: Parallel Bars

### 3.2 Rotation Groups

- 1 to 4 rotation groups
- Teams are evenly distributed across groups
- In each rotation, every group is assigned exactly **one apparatus pair**
- Groups rotate through apparatus pairs in a fixed order

---

## 4. Gymnasts & Routines

### 4.1 Participation Rules

- Every **male gymnast** may perform on **any male apparatus**
- Every **female gymnast** may perform on **any female apparatus**
- There is **no fixed assignment** of gymnasts to apparatus

### 4.2 Routine Limits

For each:

```
Team × Rotation × Apparatus × Gender
```

- **0 routines** → allowed
- **1 routine** → allowed
- **2 routines** → allowed
- **3 routines** → allowed (maximum)
- Attempting a **4th routine must be blocked** by validation

Scoring consequences:
- If 2 or more routines exist → the best 2 are counted
- If 1 routine exists → that score is counted
- If 0 routines exist → contributes 0 points for that gender/apparatus

Routines are created **dynamically on score entry**, not preconfigured.

---

## 5. Scoring Model

### 5.1 Score Components

- Difficulty score (D)
- Execution score (E)
- Neutral deductions

### 5.2 Live Calculation

- Total score is calculated as:

```
Total = D + E − Neutral
```

- Calculation is:
  - performed immediately in the frontend
  - recalculated on every value change
  - displayed read-only
- Purpose:
  - allow judges to immediately cross-check plausibility

The backend recomputes all totals independently for validation.

---

## 6. Apparatus & Judges Panel State Model

### 6.1 Judges Panel Side State

Each **judges panel side** (men or women, per rotation group and rotation) has exactly three states:

```
INACTIVE → OPEN → COMPLETED
```

#### INACTIVE
- The corresponding rotation has not yet started
- No scoring interaction is possible
- Panel side is not visible to judges

#### OPEN
- The rotation is ACTIVE
- Judges panel side may:
  - enter scores
  - edit scores
  - mark itself as completed

#### COMPLETED
- Judges panel side has been explicitly marked complete
- Judges panel side may no longer enter or edit scores

### 6.2 Re-opening Rules (Judges Panel Side)

- Re-opening is **only possible while the rotation is ACTIVE**
- Re-opening is performed **only by an organizer**
- Re-opening applies **only to a single judges panel side** (men or women)
- Re-opening transitions:

```
COMPLETED → OPEN
```

- Re-opening has **no effect** on rotation state
- Re-opening is **not possible** once the rotation is COMPLETED

---

### 6.3 Apparatus Pair State (Derived)

An **apparatus pair** is considered COMPLETED **iff**:

- the women’s judges panel side is COMPLETED **and**
- the men’s judges panel side is COMPLETED

The apparatus pair state is **derived** and has no independent transitions.

---

## 7. Rotation State Model

### 7.1 States

```
PENDING → ACTIVE → COMPLETED
```

### 7.2 Definition of a Rotation

A **rotation** represents one competition phase in which **all rotation groups** perform routines on their currently assigned apparatus pairs.

In a single rotation:
- each rotation group is assigned exactly one apparatus pair
- different groups are on different apparatus pairs
- judges panels score only the apparatus they are assigned to for the competition

### 7.3 Semantics

- **PENDING**
  - Rotation has not started
  - All judges panel sides are INACTIVE

- **ACTIVE**
  - Rotation is in progress
  - Judges panels score and complete their assigned apparatus sides

- **COMPLETED**
  - Rotation has been explicitly ended by an organizer
  - Rotation is strictly final and irreversible

### 7.4 Ending a Rotation (Organizer Action)

A rotation may be **ended only by an organizer**.

The organizer may end a rotation **only when**:

```
For every rotation group G:
  apparatusPair(rotation, G) is COMPLETED
```

Ending a rotation causes:
- `ACTIVE → COMPLETED`
- publication of scores for that rotation
- permanent lock-out of judges panels for that rotation

### 7.5 Irreversibility

Once a rotation enters the COMPLETED state:
- it can never return to ACTIVE
- no judges panel side may be reopened
- only organizer score edits remain possible

---

## 8. Team Apparatus Result Calculation

For each **team** and **apparatus pair**:

### Step 1 – Gender-Specific Collection
- Collect up to **3 scores per gender**
- Scores belong to:
  ```
  Team × Rotation × Apparatus × Gender
  ```

### Step 2 – Selection
- Sort scores descending
- Select the **best 2** scores
- If fewer than 2 scores exist, sum what is available

### Step 3 – Subtotals
- MenSubtotal = sum(best up to 2 men scores)
- WomenSubtotal = sum(best up to 2 women scores)

### Step 4 – Apparatus Pair Result

```
ApparatusPairResult = MenSubtotal + WomenSubtotal
```

Each apparatus pair result contributes **exactly once** to the team’s competition total.

---

## 9. Resu1

- Scores are **never published automatically**
- Scores for a rotation are published **only when the organizer ends the rotation**
- This rule applies uniformly to **all rotations**, including the final one

After a rotation is ended:
- results become visible to all users
- judges panels are permanently locked for that rotation

After the final rotation:
- the competition may be closed by the organizer
- the competition becomes archived

---

## 10. Offline & Real-Time Behavior

### Judges Tablets
- One device per judges panel
- Local buffering of score inputs
- Automatic retry when connectivity is restored

### Real-Time Updates
- Live propagation of:
  - score changes
  - judges panel side completion
  - rotation readiness
  - rotation completion and publication

---

## 11. Non-Goals (Explicitly Out of Scope)

- Multiple concurrent competitions
- Individual judge attribution
- Score history or versioning UI
- Generic, configurable gymnastics rules engine
- Tie-break rules (shared ranks only)

---

## 12. Planning Status

This document represents a **closed and internally consistent planning baseline** reflecting all clarifications to date, including fairness constraints on judges panel usage.

Future additions may include:
- test competition walkthroughs
- UX refinements
- stress and failure-mode scenarios

These may be added later **without reopening core design decisions**.

End of document.
