#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Add the Bipolar Inventory of Signs and Symptoms Scale (BISS, Bowden v1.5 4/1/08)
to data.json.

Idempotent: re-running replaces the BISS structures in place. Supports --check
(dry run, prints what would be written and exits non-zero if a write is needed).

Provenance / licensing
----------------------
BISS is copyright 2005 Charles L. Bowden, MD. The printed form states that no
part may be reproduced without written permission, BUT that "researchers and
clinicians working in nonprofit or publicly owned settings (including
universities, nonprofit hospitals, and government institutions) may make single
copies of a BISS instrument for their own use." That permission is recorded on
the scale object so the deployment context can be checked before use.

Scoring rules encoded here (verbatim from the manual):
  * every item 0-4 over the most recent 7 days, using self-report plus family
    and clinician observation;
  * anchor statements are examples of behaviour / proportion of time / severity
    / functional impairment, not an exhaustive list;
  * items are rated on frequency AND severity; a score of 3 usually entails
    behaviour observable to others; 0 = symptom completely absent;
  * when in doubt between two ratings, assign the HIGHER score;
  * rate each item independently (e.g. 9 psychomotor slowing and 22 agitation
    can both be positive if they occurred at different times);
  * section I Depression = items 1-20, section II Mania = items 21-44.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data.json")

BIPOLAR_DISORDERS = ["bipolar_i_disorder", "bipolar_ii_disorder",
                     "bipolar_depressive", "other_specified_bipolar"]


def bi(name, en, hi=None):
    d = {"en": en}
    if hi:
        d["hi"] = hi
    return d


# ---------------------------------------------------------------- anchors ----
# Verbal anchors transcribed from the printed form (page N of 7). Each item
# carries its OWN anchor list because the wording differs per item.
A = lambda *xs: [{"v": i, "en": x} for i, x in enumerate(xs)]

ANCHORS = {
    1: A("Not at all",
         'Slight; e.g., only occasionally feels "sad" or "down"',
         'Mild; e.g., often feels somewhat "depressed," "blue" or "downhearted," and/or appears sad and is less responsive to positive stimulus',
         'Moderate; e.g., most of the time feels "depressed," and/or several manifestations of sadness with limited ability to brighten up',
         'Severe; e.g., most of the time feels "wretched," sustained gloomy appearance'),
    2: A("Not at all",
         "Slight; e.g., looks dispirited, but brightens up easily",
         "Mild; e.g., more physical manifestations of sadness, and less response to positive stimulus",
         "Moderate; e.g., often appears sad and unhappy",
         "Severe; e.g., extreme and continuous gloom and despondency"),
    3: A("Not at all",
         "Slight; e.g., occasional feelings of discouragement about future",
         "Mild; e.g., often somewhat discouraged",
         "Moderate; e.g., very often feels quite pessimistic about the future",
         "Severe; e.g., pervasive feelings of intense pessimism"),
    4: A("Not at all",
         'Slight; e.g., occasional thoughts of death (without suicidal thoughts), "I would be better off dead" or "I wish I were dead."',
         "Mild; e.g., frequent thoughts of being better off dead or occasional thoughts of suicide but has no plan or intent",
         "Moderate; e.g. often thinks of suicide or has thought of a specific method",
         "Severe; e.g. often thinks of suicide and has thought of a specific plan or has made a suicidal gesture or attempt"),
    5: A("Not at all",
         "Slight; e.g., occasionally worries about some realistic or trivial problem",
         "Mild; e.g., often worries excessively about a problem",
         "Moderate; e.g., very often worries excessively about a realistic or trivial problem",
         "Severe; e.g., most of the time is spent in worrying or brooding about problems which he/she cannot dispel"),
    6: A("Not at all",
         "Slight; e.g., occasional feelings of mild self-blame",
         "Mild; e.g., often feels somewhat guilty about past actions, the significance of which are exaggerated, such as consequences of the illness",
         "Moderate; e.g., often feels quite guilty about past actions or feelings of guilt that cannot be explained",
         "Severe; e.g., pervasive feelings of intense guilt, self-reproach or generalizes feelings of self-blame"),
    7: A("Not at all",
         "Slight; e.g., occasional feelings of inadequacy",
         "Mild; e.g., often feels somewhat inadequate",
         "Moderate; e.g., often feels like a failure",
         "Severe; e.g., pervasive feelings of worthlessness"),
    8: A("Not at all",
         "Slight; e.g., occasional less energy than usual",
         "Mild; e.g., at times definitely more tired, or less energy than usual",
         "Moderate; e.g., most of time is very tired, lacking energy",
         "Severe; e.g., spends most of time resting, nearly always feels fatigued"),
    9: A("Not at all",
         "Slight, of doubtful clinical significance, only subjective feeling of being slowed",
         "Mild; e.g., conversation is noticeably retarded but not strained",
         "Moderate; e.g., conversation is strained, or moves very slowly",
         "Severe; e.g., conversation is difficult to maintain, or hardly moves at all"),
    10: A("Not at all",
          "Slightly reduced ability to enjoy usual interests. Reduced ability to feel anger",
          "Mild; e.g., loss of interest in the surroundings/activities, loss of feelings for friends and acquaintances",
          "Moderate; e.g., most of the time has moderately reduced interest in most pleasurable activities",
          "Severe; e.g., feels emotionally paralyzed, inability to feel anger or grief, and a complete or even painful failure to feel for close relatives and friends"),
    11: A("Not at all",
          "Slight reduction in interest in social interaction",
          "Mild; e.g., actual reduction in social interaction, associated with some avoidance of others",
          "Moderate; e.g., substantially reduced time spent with others, with some adverse consequences to the social avoidance",
          "Marked reduction in social interactions, with consequent difficulties in relationships with family, friends, peers"),
    12: A("Not at all",
          "Slight; sexual interest is reduced",
          "Mild; e.g., definite reduction of sexual interest. Usual sexual activities partially reduced",
          "Moderate; e.g., persistent reduction of sexual interest. Usual sexual activities reduced consistently",
          'Severe; e.g., complete sexual indifference. "I have no interest in sex."'),
    13: A("Not at all",
          "Slight; e.g., fleeting inner tension",
          "Mild; e.g., periods of tension, fear that can be mastered",
          "Moderate; e.g., tense, ill at ease most of the time, minimal ability to control tension, fear",
          "Severe; e.g., tense, fearful, frequent anxiety attacks. Often functionally incapacitating"),
    14: A("Not at all",
          "Slight; occasional or slight autonomic disturbances such as flushing or sweating under stress",
          "Mild; e.g., autonomic disturbance on several occasions, even when not under stress",
          "Moderate; e.g., tense, ill at ease most of the time, minimal ability to control tension, fear",
          "Severe; e.g., tense, fearful, frequent anxiety attacks. Often functionally incapacitating."),
    15: A("Not at all",
          "Slight; e.g., occasionally palms sweat excessively",
          "Mild; e.g., often has 1 or more physical symptoms to a mild degree",
          "Moderate; e.g., often has several symptoms or 1 symptom to a considerable degree",
          "Severe; e.g., very frequently bothered by 1 or more symptoms or 1 symptom to a severe degree"),
    16: A("Not at all",
          "Slight, occasional feelings of fear that quickly abate",
          "Mild, e.g.; occasional fear that persists despite efforts to control",
          "Moderate, e.g., fearful most days, sometimes associated with retreating or hostile reaction",
          "Severe, e.g.; quite fearful most days, much of day. Unable to control fear, or at least one intensely fearful experience."),
    17: A("No experience of insomnia during rating period",
          "Slight; e.g., occasional difficulty with insomnia.",
          "Mild; e.g., often has some significant difficulty",
          "Moderate; e.g., usually has considerable difficulty",
          "Severe; e.g., almost always has great difficulty"),
    18: A("No excessive sleep during this period",
          "Slight; sleeps longer than usual 1-2 nights/week",
          "Mild; sleeps 2-3 hours extra most days",
          "Moderate; e.g., spends part of day asleep in spite of normal or increased sleep at night",
          "Severe; sleep increased by 4 or more hours, difficulty getting out of bed, despite excessive duration of sleep"),
    19: A("No change at all",
          "Slight decrease, questionable clinical significance",
          "Mild decrease in appetite",
          "Moderate decrease in appetite associated with change in weight",
          "Severe loss of appetite, e.g., no appetite, significant weight loss"),
    20: A("Not at all",
          "Slight increase, questionable clinical significance",
          "Mild increase in appetite",
          "Moderate loss of control over eating and/or increase in appetite associated with change in weight",
          "Severe increase (loss of control over eating or significant weight gain)"),
    21: A("Not at all",
          "Slight; e.g., occasional difficulties in collecting one's thoughts",
          "Mild; e.g., difficulties in concentrating and sustaining thought, which at times interferes with reading or conversation",
          "Moderate; e.g., most of time has impaired concentration, and usual responsibilities and actions are hampered by this",
          "Severe; e.g., incapacitating lack of concentration"),
    22: A("Not at all",
          "Slight, and of doubtful clinical significance",
          "Mild; e.g., occasionally fidgety or unable to sit quietly in a chair",
          "Moderate; e.g., often pulling at hair, clothing, etc or having to move",
          "Severe; e.g., constantly fidgety or pulling at hair, clothing, etc or pacing up and down"),
    23: A("Not at all",
          "Slight and of doubtful clinical significance",
          "Mild; e.g., definitely more irritable than called for by the situation but only occasional and not intense",
          "Moderate; e.g., often feelings quite angry or occasionally feels very angry",
          "Severe; e.g., most of the time quite angry or often feels very angry"),
    24: A("Not at all",
          "Slight and of doubtful clinical significance",
          "Mild; e.g., definitely more irritable than called for by the situation but only occasional and not intense",
          "Moderate; e.g., often displays anger",
          "Severe; e.g., most of the time displays intense anger"),
    25: A("Not at all",
          "Slight and of doubtful clinical significance",
          "Mild; e.g., loud, sarcastic, at times, but only occasionally",
          "Moderate; e.g., often demanding or loud",
          "Severe; e.g., most of time somewhat demanding, loud, or any episode of shouting, hitting, breaking"),
    26: A("Not at all",
          "Slightly more interest in activities, but of questionable significance",
          "Mild increase in activity level",
          "Moderate increase in activity",
          "Marked increase, almost constantly involved in numerous activities in many areas"),
    27: A("Not at all",
          "Slightly more energetic but of questionable significance",
          "Mild increase in energy. Less fatigued than usual.",
          "Moderate increase in energy compared to usual, with little or no fatigue",
          "Markedly more energetic than usual, all or nearly all of time, with little or no fatigue"),
    28: A("Not at all",
          "Slight increase in interest in social interaction.",
          "Mild; actual increase in social interaction, associated with actively seeking out others",
          "Moderate; substantially increased time spent with others, causing minor impairment, e.g., inappropriate renewing of old acquaintances",
          "Marked increase in social interactions, associated with intrusive, unwanted interactions, contacts strangers"),
    29: A("Not at all",
          "Slight; e.g., feels talkative",
          "Mild; e.g., free, lively associations, not interfering with person's staying on track",
          "Moderate; e.g., rapid flow of ideas, with difficulty returning to primary theme of thoughts",
          "Severe; e.g., constantly feels thoughts racing, has great difficulty collecting thoughts and returning to main focus"),
    30: A("Not at all",
          "Slight; e.g., tendency to talk excessively, not impairing",
          "Mild; e.g., rapid, verbose speech. Gives detailed answers",
          "Moderate; e.g., garrulous, difficult to interrupt",
          "Severe; e.g., speaking almost constantly. Words come tumbling out. Cannot be interrupted most of time."),
    31: A("Not at all",
          "Slight increase in sexual interest",
          "Mild increase in sexual interest, e.g., fantasies that at times preoccupy patient",
          "Moderate; e.g., definite increase in sexual interest or activities, or intrusive sexual fantasies",
          "Severe; e.g., preoccupied with sexual fantasies. Marked increase in sexual activities"),
    32: A("No reduced need for sleep in past week",
          "Slight; up to 1 hour less than usual",
          "Mild; up to 2 hours less than usual",
          "Moderate; up to 3 hours less than usual",
          "Severe; 4 or more hours less than usual"),
    33: A("Not at all",
          "Slight; e.g., is more expansive, confident than most people in similar circumstances",
          "Mild; e.g., definitely inflated self-esteem or exaggerates talents somewhat out of proportion to circumstances",
          "Moderate; e.g., inflated self-esteem clearly out of proportion to circumstances",
          "Severe; e.g., grandiosity also may have delusional component"),
    34: A("Not at all",
          "Slight; e.g., good spirits more cheerful than most people in similar circumstances, but of only doubtful clinical significance",
          "Mild; e.g., definitely elevated mood and optimistic outlook that is somewhat out of proportion to the circumstances",
          "Moderate; e.g., mood and outlook are clearly out of proportion to circumstances",
          "Severe; e.g., quality of euphoric, exalted mood"),
    35: A("Not at all",
          "Slight; e.g., brief periods of thinking more clearly or creatively",
          "Mild increase in clarity or creativity of thought",
          "Moderate increase; e.g., believes that has important insight into personal or external affairs but, with real evidence for this",
          "Marked; e.g., most of time thinking seems exceptionally clear, creative, may be associated with some adverse consequence, e.g., acts on basis of belief in plans, but without reasonable chance of success in action taken"),
    36: A("Not at all",
          "Slight; e.g., frequently has more energy, interests in evening that delay time of getting to bed by up to 1 hour",
          "Mild; e.g., most evenings takes on activities that delay time getting to sleep by up to 2 hours, feels more energized most evenings/nights with difficulty calming down. Has difficulty discontinuing activities at night.",
          "Moderate; e.g., definite impairment from increased diurnal energy, interests in evenings. Stays up, active beyond midnight. Sleep delayed by over 2 hours.",
          "Severe; e.g., marked interference with time that sleep period starts, and interference with ordinary daytime activities due to elevated energy, activity, or interests in the evening/night"),
    37: A("Not at all",
          "Slight; e.g., occasional impulsive action with little or no adverse consequences",
          "Mild; e.g., frequent mildly impulsive actions with some adverse consequences, e.g., mild speeding, cutting in line",
          "Moderate; e.g., frequent impulsive actions, with actual or realistic potential for adverse consequences such as firing, legal charge, traffic ticket. Impulsivity is evident during the interview",
          "Severe; serious impairment from impulsivity; e.g., accident with medical consequences, ticketed by the police"),
    38: A("Not at all",
          "Slight; e.g., attention occasionally distracted by irrelevant stimuli, such as background noises",
          "Mild; e.g., easily distracted, but returns to primary theme without prompting",
          "Moderate; e.g., relatively frequent distraction, has difficulty getting back on track, even with prompting",
          "Severe; e.g., continually distracted by incidental events and objects, which makes interviewing difficult"),
    39: A("Not at all",
          "Slight; e.g., thoughts of promiscuous behavior, moderately aggressive driving",
          "Mild; e.g., places self in situations with some risk for injury, attention by police, contracting communicable disease",
          "Moderate; e.g., frequent risk taking, with at least one serious risk taking action",
          "Severe; e.g., argues with officials without provocation, runs red lights, solicits sex"),
    40: A("Not at all",
          "Slight; e.g., occasional periods of fluctuating mood, affects, generally within a day, of questionable clinical significance",
          "Mild; e.g., frequent mild, mood instability or lability which family, close associates see as dysfunctional",
          "Moderate; e.g., definite impairment in social, work role function from frequent mood instability",
          "Serious impairment from mood lability. Persists most of day, most days, interferes with most social, work, role functions"),
    41: A("Not at all",
          "Slight feelings of distrustfulness which may be realistically based and are of doubtful clinical significance",
          "Mild; suspiciousness definitely not warranted by the situation, but only occasional and of mild intensity, e.g., often feels taken advantage of",
          "Moderate; often suspicious or distrustful, but clearly ideas of reference that are recognized as the imagination",
          "Severe; pervasive suspiciousness, or persecutory feelings of delusional intensity, e.g., plot may exist against him/her"),
    42: A("Not at all",
          "Slight; suspected or likely, but not impairing",
          "Mild; delusion definitely present, but at times subject questions it as a false belief",
          "Moderate; delusion has a significant effect on thoughts, feelings, actions, e.g., asks family to forgive sins, preoccupied with belief that he or she has special power.",
          "Severe; delusions have major impact on patient or others, e.g., has delusions of control, calls emergency number about space invaders"),
    43: A("Not at all",
          "Slight; occasional altered perception of doubtful clinical significance",
          "Mild; definitely present, but is generally aware that it is imagination and is usually able to ignore it",
          "Moderate; generally believes in the reality of the hallucination, but it has little influence on behavior",
          "Severe; convinced the hallucination is real and it has significant effects on actions, e.g., locks doors to keep heard pursuers away"),
    44: A("Not at all; insight is present, patient admits, understands illness and need for treatment",
          "Slight impairment; patient feels he/she is ill, or needs treatment, but has little insight into history of illness or what characterizes the illness.",
          "Mild; admits behavior is changed, or need for treatment, but attributes it to a nonpsychiatric external factor (i.e., marital conflict, stress). Factors are plausible and non-delusional.",
          "Moderate impairment; admits behavior is changed, or need for treatment, but gives implausible or delusional explanations",
          "Severe; denies behavior change, illness, or need for treatment"),
}

# --------------------------------------------------------------- item text ----
# name = printed item title, definition = printed item description,
# probes = printed bold/italic probe questions (bold first).
ITEMS = [
    # ---- Section I. DEPRESSION (1-20) ----
    dict(n=1, sec="D", name="Sadness - reported", safety=True,
         defn='Subjective feeling of depression based on verbal complaints of feeling depressed, sad, blue, gloomy, down in the dumps, empty, "don\'t care." Do not include such ideational aspects as discouragement, pessimism, or worthlessness; suicide attempts or depressed appearance.',
         probes=["During the past 7 days, how have you been feeling? Describe your mood?",
                 "Have you felt depressed (sad, blue, moody, down, empty, as if you didn't care)?",
                 "Have you cried or been tearful? How often? Does it come and go? How long does it last? How bad is the feeling? Can you stand it?"]),
    dict(n=2, sec="D", name="Sadness - observed",
         defn="Appears despondent, gloomy, despairing, as reflected in speech, facial expression, and posture. Rate also by inability to brighten up.",
         probes=["Have others commented that you appeared sad, blue, or unhappy?"]),
    dict(n=3, sec="D", name="Pessimism",
         defn="Discouragement, pessimism and hopelessness.",
         probes=["Have you been discouraged (pessimistic, felt hopeless)?",
                 "What kind of future do you see for yourself?",
                 "How do you think things will work out?",
                 "Can you see yourself or your situation getting any better?"]),
    dict(n=4, sec="D", name="Suicidality", safety=True,
         defn="Suicidal tendencies, including preoccupation with thoughts of death or suicide. Do not include mere fears of dying.",
         probes=["When a person gets upset, depressed, or feels hopeless, he or she may think about dying or even killing themselves. Have you had any such thoughts?",
                 "Have you thought about how you would do it?",
                 "Have you told anybody about suicidal thoughts?",
                 "Have you actually done anything?"]),
    dict(n=5, sec="D", name="Worry",
         defn="Worrying, brooding, painful preoccupation and inability to get mind off unpleasant thoughts (may or may not be accompanied by depressive mood).",
         probes=["Have you been worrying a lot?",
                 "How much do you worry? What kinds of things have you been worrying about?",
                 "How much of your time is spent in this?",
                 "Are you able to get your mind off it?"]),
    dict(n=6, sec="D", name="Guilt",
         defn="Feelings of self-reproach or excessive, inappropriate guilt for things done or not done.",
         probes=["Do you blame yourself for anything you have done or not done?",
                 "What about feeling guilty?",
                 "Do you feel you have done anything wrong?",
                 "Do you deserve punishment?",
                 "Do you feel you have brought this on yourself?",
                 "Have you been critical of yourself?"]),
    dict(n=7, sec="D", name="Feelings of inadequacy",
         defn="Negative evaluation of him or herself, including feelings of inadequacy, failure, worthlessness.",
         probes=["How has your self-esteem been this past week?",
                 "Are you down on yourself?",
                 "What is your opinion of yourself compared to other people?",
                 "Worthless? A failure? How often do you feel this way about yourself?"]),
    dict(n=8, sec="D", name="Low energy",
         defn="Difficulty getting started, or slowness initiating and performing everyday activities. Subjective feeling of lack of energy or fatigue. Do not rate lack of interest.",
         probes=["Have you had less energy than usual to do things? Have you been getting tired easily? I am not talking about your interest in things, but your physical energy to do things.",
                 "Has this interfered with your accomplishing tasks that you ordinarily need to do? Have you needed help in getting started?"]),
    dict(n=9, sec="D", name="Psychomotor slowing",
         defn="Generalized slowing down of physical reactions, movements, and speech, including latency in speech. Rate both on observed and reported information.",
         probes=["Have you been slowed down, not able to move as quickly as usual?",
                 "Did you find it hard to start talking?",
                 "Did you talk a lot less than usual?",
                 "Did you feel like you were moving in slow motion?"]),
    dict(n=10, sec="D", name="Loss of interest",
         defn="Subjective experience of reduced interest in the surroundings, or activities that normally give pleasure. Reduced ability to react with adequate emotion to circumstances or people.",
         probes=["When you participated in activities that you usually enjoy, were they pleasurable for you?",
                 "If you did not do any of your usual activities, was this because you did not have the opportunity? (If the answer is opportunity, do not rate towards loss of interest.)",
                 "Can you experience your usual feelings for your loved ones?"]),
    dict(n=11, sec="D", name="Social withdrawal",
         defn="Reduced interest in and attention to others. Associated with reduced social interactions, and reduced time spent with others.",
         probes=["Have you had less interest in spending time with other people, including your family members, friends, or persons you work with?",
                 "Did you actually spend less time interacting with others?",
                 "How much less time than usual for you does this represent?",
                 "Did you avoid social contact with people whom you normally interact with?"]),
    dict(n=12, sec="D", name="Reduced sex drive",
         defn="Reduced sexual interest, fantasies, or a reduction of sexual activity. Judge against the subject's usual sexual interests and habits when well.",
         probes=["What has your sexual interest and activity been like this past week?",
                 "Has it been reduced at any time?",
                 "Can you tell me an example of the way it has changed, been low?"]),
    dict(n=13, sec="D", name="Anxiety - reported",
         defn="Subjective feelings of anxiety, fearfulness, or apprehension, whether or not accompanied by somatic anxiety and whether focused on specific concerns or not.",
         probes=["Have you felt tense or anxious?",
                 "Does this get to the point that you feel uncomfortable?",
                 "Have you had anxiety attacks?",
                 "Are you able to control these feelings?"]),
    dict(n=14, sec="D", name="Anxiety - observed",
         defn="Autonomic over-activity and/or muscle tension, expressed in facial appearance, flushing, sweating, cold hands, posture, movements.",
         probes=["Over the past week have others commented that you appeared tense or showed signs of anxiety, such as sweating or clammy hands?"]),
    dict(n=15, sec="D", name="Somatic anxiety - reported",
         defn="Has been bothered by 1 or more physiological concomitants of anxiety.",
         probes=["Have you been bothered by physical symptoms like palpitations, shortness of breath, sweating, headaches, stomach cramps, diarrhea or muscle tension?",
                 "If yes, determine if there were other symptoms and the overall severity of the disturbance."]),
    dict(n=16, sec="D", name="Fearfulness",
         defn="Alerting response associated with perceived unfamiliar or threatening sound, visualization, event or smell, coupled with autonomic arousal (increased pulse, heavy breathing), impulse to retreat or attack.",
         probes=["Some people feel frightened easily when unpleasant events take place around them. Has that happened to you in the past week?",
                 "What about feeling frightened unexpectedly?",
                 "Has the degree that you have been frightened been more than when you are feeling well?",
                 "How have you felt inside when this has happened?",
                 "How well have you been able to control the fear?"]),
    dict(n=17, sec="D", name="Insomnia",
         defn="Sleep disturbance, including initial, middle and terminal difficulty in getting to sleep or staying asleep or waking up earlier than usual. Take into account the estimated number of hours slept and subjective sense of lost sleep. Do not rate decreased need for sleep.",
         probes=["Are you taking any medication to help you sleep?",
                 "How has your sleep been this last week?",
                 "Did you have any difficulty getting to sleep? How many hours a night were you able to sleep even when tired?",
                 "How many days did you have difficulty sleeping?",
                 "How does that compare with a usual full night of sleep for you?"]),
    dict(n=18, sec="D", name="Excessive sleep",
         defn="Increased duration of sleep, compared to the subject's own normal pattern when well. The questions for item 17 will aid in rating this item. It is possible that a patient could receive a positive score for both item 17 and 18. Rate independent of whether person is taking a drug that might alter sleep.",
         probes=["During the past week, have you overslept in the morning?",
                 "Do you take naps during the day?",
                 "Do you ever have difficulty getting out of bed?",
                 "How many more hours sleep have you been getting than usual?"]),
    dict(n=19, sec="D", name="Reduced appetite",
         defn="Appetite compared to usual.",
         probes=["Has your appetite for food changed in the last week compared to the way it usually is?",
                 "Have you eaten less than you usually do?",
                 "Do you have to force yourself to eat?",
                 "Do other people have to urge you to eat?",
                 "Over the past month, has your weight changed? By how much?"]),
    dict(n=20, sec="D", name="Increased appetite",
         defn="Increase in appetite and/or binge eating.",
         probes=["Have you eaten more than you usually do?",
                 "Are you able to control how much you eat?",
                 "Have you binged on any foods?",
                 "Have you eaten snacks between regular meals? Appetite associated with change in weight?",
                 "How much of the time have you binged, eaten snacks, etc?"]),
    # ---- Section II. MANIA (21-44) ----
    dict(n=21, sec="M", name="Impaired concentration",
         defn="Difficulty in collecting one's thoughts, mounting to incapacitating lack of concentration. Rate frequency, intensity and degree of incapacity produced.",
         probes=["How well have you been able to concentrate?",
                 "Are there any times when your concentration has been below your normal level?",
                 "Has this interfered with your reading, work, making conversation with others?"]),
    dict(n=22, sec="M", name="Agitation",
         defn="Purposeless motor activity. Inability to sit still, pacing, fidgeting, wringing hands, pulling at clothes, movement of lips or fingers. Do not include feeling of tension or restlessness. Rate observed and reported behavior.",
         probes=["Were there times when you were unable to sit still? Did you feel like you had to be constantly pacing up and down?",
                 "Did you notice that you were pulling on your clothing, hair, or skin? Did you wring your hands? How frequently did you do this? Did it cause you any difficulties in the way you functioned?"]),
    dict(n=23, sec="M", name="Irritability - reported",
         defn="Subjective feeling of anger, resentment, or annoyance (directed externally) whether expressed overtly or not. Rate only the intensity and duration of the subjective sense of irritability.",
         probes=["How irritated, angry, or resentful have you felt - whether you showed it or not?",
                 "How strongly did you feel this way? How much of the time did you feel this way? How did you show your (anger, annoyance, irritability)?"]),
    dict(n=24, sec="M", name="Irritability - observed",
         defn="Overt expression of irritability, annoyance and anger. Do not rate subjective feelings of annoyance, anger, or irritability on this item, no matter how intense, unless it is expressed overtly. Include any irritability observed by others.",
         probes=["Over the past week, have you expressed your irritation or anger to others? How often did that occur?"]),
    dict(n=25, sec="M", name="Aggressive behavior", safety=True,
         defn="Confrontational, argumentative behavior.",
         probes=["During the past week, have there been any times when you were loud, demanding, or sarcastic?",
                 "Did you have any arguments or confrontations with people?",
                 "Did you lose your temper when the above occurred? Did you throw or break anything? Did you push or hit anyone?"]),
    dict(n=26, sec="M", name="Hyperactive",
         defn="Increase in goal-directed activity as compared with usual level. Consider changes in involvement or activity level associated with work, family, friends, sex drive, projects, interests or activities (e.g., telephone calls, letter writing). Note that this item rates behaviour that may not have associated impairment of function or adverse consequences.",
         probes=["Have you been more active or involved in things than usual?",
                 "What about your work, housekeeping, family, friends, sex, hobbies, new projects or interests? How much of your day has been spent on this?"]),
    dict(n=27, sec="M", name="Energetic",
         defn="Unusually energetic, more active than the usual level without expected fatigue.",
         probes=["Have you had more energy than usual to do things?",
                 "More than just a return to normal or usual level?",
                 "Did it seem like too much energy?"]),
    dict(n=28, sec="M", name="Increased social interest",
         defn="Increased interest in, attention to others. Associated with increased social interactions and time spent with others.",
         probes=["Have you had more interest than usual in spending time with other people, including church, family, friends, co-workers?",
                 "Did you actually spend more time interacting with others?",
                 "How much more time than usual for you does this represent?",
                 "Did you make social contact with people whom you do not know or have not seen in a long time? What about talking on the phone, or using the internet for conversations?"]),
    dict(n=29, sec="M", name="Racing thoughts - reported",
         defn="Rapid flow of ideas, which may be observable in speech. There is continuity of thought, although it may be difficult or impossible to stay on track with the content. Rate on subjective report.",
         probes=["Have you been bothered by having too many thoughts at once?",
                 "Have your thoughts been speeded up?",
                 "Has this caused any difficulties in staying on track?",
                 "How much of the time has this happened? Is it moderate or severe over the past week?",
                 "How different was that from when you are feeling normal?"]),
    dict(n=30, sec="M", name="Pressured speech",
         defn="Pressure of talk, increased flow of speech, overly loquacious. Rate both observed and reported behavior.",
         probes=["Have you experienced yourself talking too fast, saying too much in conversations?",
                 "Did others have to interrupt to get a word in?",
                 "Has this interfered with your effectiveness in conversations?"]),
    dict(n=31, sec="M", name="Increased sexuality",
         defn="Stronger sexual interest than usual. May be reflected in an increase in sexual activities or fantasies. Judge in comparison with subject's usual sexual habits when well.",
         probes=["How has your interest in sexual activities been the past week?",
                 "Have you thought about, or talked about sexual matters more than usual?",
                 "What has your level of sexual activity been?"]),
    dict(n=32, sec="M", name="Less need for sleep",
         defn="Less need for sleep during the past week. A patient could be scored positive on this item as well as items 17 and 18 for impaired sleep.",
         probes=["Have you needed less sleep than usual to feel rested?",
                 "How many hours did you sleep? How many days in the last week did you have a reduced need for sleep? How much sleep do you ordinarily need?"]),
    dict(n=33, sec="M", name="Grandiose",
         defn="Increased self-esteem and appraisal of his/her worth, contacts, power or knowledge (up to grandiose delusions) as compared with usual level. Persecutory delusions should not be considered evidence of grandiosity unless the subject feels the persecution is due to some special attributes of his/hers (e.g., power, contacts.)",
         probes=["Have you felt more self-confident than usual?",
                 "Have you felt that you are a particularly important person, or that you have special talents, abilities?",
                 "What about special plans?"]),
    dict(n=34, sec="M", name="Elated",
         defn="Elevated mood and/or optimistic attitude toward the future, out of proportion to the circumstances.",
         probes=["Have there been times when you felt very good or too cheerful or high - not just your normal self?",
                 "Did you feel on top of the world or as if there was nothing you couldn't do?",
                 "Have you felt that everything would work out just the way you wanted?"]),
    dict(n=35, sec="M", name="Sharpened thinking",
         defn="Has experienced unusually sharp and clear thinking, associated with creativity, problem solving capabilities.",
         probes=["Have there been periods when your thinking seemed especially clear during the week?",
                 "Do you recall having had any unusually creative ideas or approaches to problems?"]),
    dict(n=36, sec="M", name="Elevated evening energy, interests",
         defn="Increases in energy, activity, or interests in evening/night period.",
         probes=["Has your energy, activity or interests been about the same throughout the day?",
                 "Have you had any tendency to be particularly active or take on projects in the evening or at night?",
                 "Have you had more energy during the evening or nighttime?",
                 "Have these kept you up past your usual hour of going to bed, or beyond midnight?",
                 "Has it ever been difficult to stop what you are doing, e.g., reading, TV, project at night?"]),
    dict(n=37, sec="M", name="Impulsive",
         defn="Makes decisions, starts actions without considering consequences. Impulsivity may be associated with intrusiveness, spending, criticism of others, sexual behavior.",
         probes=["Have you made any decisions without thinking the situation through?",
                 "Have you made any snap judgments? Have you talked when you should have kept quiet or taken on a project without thinking it through?",
                 "Have you been able to control your responses when placed in a situation where a decision or choice is needed? Have you been patient or impatient when you have had to stand in line, say at a check out counter? Have you cut in line?",
                 "Have you bought things that you did not need?"]),
    dict(n=38, sec="M", name="Distractible",
         defn="Attention easily diverted by external stimuli. Rate principally on observed behavior.",
         probes=["Do you notice that your attention shifts to other things taking place around you?",
                 "Have you been easily distracted by your surroundings?",
                 "Have you found this causing you to have difficulty in staying on a subject in conversation, or to concentrate?"]),
    dict(n=39, sec="M", name="Risky behavior", safety=True,
         defn="Involvement in activities with high potential for adverse consequences socially, legally, financially or sexually.",
         probes=["Have you done anything that was risky or got you in trouble?",
                 "Have spent more than you can afford? Have you told someone off unnecessarily, driven too fast, or done any other things that could have gotten you into trouble? Have you used any drugs that could be harmful to you?",
                 "How often has this occurred over the past week? Can you give an example?"]),
    dict(n=40, sec="M", name="Affective lability",
         defn="Reported and observed spontaneous sharp shifts of affective or mood states lasting from minutes to hours. Lability may or may not be influenced by circumstances. Often described metaphorically: \"I am on a roller coaster, I am like a yo yo.\" Affects can be sad, giddy, angry, or over confident. Do not rate on basis of what affective states are expressed. Rate on proportion of time with lability, degree of inability to control affective shifts.",
         probes=["How steady has your mood been?",
                 "Do your emotions shift fairly suddenly at times?",
                 "How much of the time are you this way? When this happens can you put a halt to it? Does it interfere in your daily life?"]),
    dict(n=41, sec="M", name="Persecutory ideas",
         defn="From slight distrustfulness through suspiciousness and delusions of persecution. Does not include feelings or beliefs which are completely justified by the situation.",
         probes=["Have people been making life hard or deliberately causing you trouble or trying to hurt you?",
                 "Have you had to be on guard with people?",
                 "Have you felt distrustful of others, or afraid that they would take advantage of you? Have you felt that you have been singled out, or targeted for their actions against you?"]),
    dict(n=42, sec="M", name="Delusions",
         defn="Severity of delusions of any type - consider conviction in delusion, preoccupation, and effect on actions. Ask questions appropriate to eliciting delusional ideation.",
         probes=["Has your imagination been playing tricks on you in any way?",
                 "Have you had any ideas that other people might not understand?",
                 "Did you think this was your imagination?",
                 "Have you felt controlled by an outside power?",
                 "What did you do about it?"]),
    dict(n=43, sec="M", name="Hallucinations", safety=True,
         defn="Severity of hallucinations of any type. Consider conviction in reality of hallucination, preoccupation, and effects on behaviors. Ask questions appropriate to eliciting hallucinations.",
         probes=["Have you heard voices or other things that weren't there or that other people couldn't hear?",
                 "Has there been anything unusual about the way things looked or sounded or smelled?",
                 "Do you think this was your imagination?",
                 "What did you do about it?"]),
    dict(n=44, sec="M", name="Impaired insight",
         defn="Awareness, understanding of his/her emotional illness, aberrant behavior, and corresponding need for psychiatric treatments.",
         probes=["Why are you coming for psychiatric treatment?",
                 "Do you feel that you currently have an emotional problem, or mental illness?",
                 "Do you believe that you need psychiatric treatment?",
                 "How would you explain your (behavior, symptoms, etc)?"]),
]

DEP_IDS = ["biss_%d" % i["n"] for i in ITEMS if i["sec"] == "D"]
MAN_IDS = ["biss_%d" % i["n"] for i in ITEMS if i["sec"] == "M"]


def build_scale():
    parts = []
    for sec, pid, pname in (("D", "biss_sec_d", "I. Depression (items 1-20)"),
                            ("M", "biss_sec_m", "II. Mania (items 21-44)")):
        qs = []
        for it in ITEMS:
            if it["sec"] != sec:
                continue
            q = {
                "id": "biss_%d" % it["n"],
                "itemNumber": it["n"],
                "text": bi(None, "%s: %s" % (it["name"], it["defn"])),
                "itemName": bi(None, it["name"]),
                "definition": bi(None, it["defn"]),
                "probes": [bi(None, p) for p in it["probes"]],
                "anchors": [bi(None, a["en"]) for a in ANCHORS[it["n"]]],
            }
            if it.get("safety"):
                q["safety"] = True
            qs.append(q)
        parts.append({"id": pid, "partKey": sec,
                      "name": bi(None, pname), "questions": qs})

    return {
        "id": "biss",
        "name": bi(None, "Bipolar Inventory of Signs and Symptoms Scale (BISS)",
                   "बाइपोलर लक्षण एवं रोगलक्षण मापनी (BISS)"),
        "type": "matrix",
        "administeredBy": "clinician",
        "optionalAssessment": True,
        "sourceInstrument": "BISS",
        "targetAge": ["adult", "adolescent"],
        "directions": bi(None,
            "Items are scored from 0 to 4, based on the most recent 7 day period, utilizing information from self report, and family and clinician observation both outside and during the interview. The anchor statements are examples of behaviors, proportions of time experiencing disturbance, severity of disturbance, and functional impairment that would qualify for a specific score, but do not exclude similar behaviors and internal feelings that would qualify for that score. Items are scored both on the basis of frequency and severity. A score of 3, in most cases, also entails behavior that is observable to others. A score of 0 means the symptom is completely absent. When in doubt between 2 ratings, assign the higher score. Some items in the mania section, e.g. No. 26, Hyperactive, rate behavior that may not have associated impairment of function or adverse consequences. For each defined item, please ask the bolded questions as they are written, or nearly so, for purposes of increasing the consistency of patient responses. The questions in italics are to be asked only if the patient indicates some symptomatology on the bolded general question(s) for the item. Additional questions to those in italics may be needed to establish item severity for individual patients. Rate each item independently. For example, a patient could have both psychomotor slowing (9) and agitation (22) if the behaviors occurred at different times over the rating period. When asking the questions for the item at the top of each page, start with the phrase, \"Over the past week have...\" The Scale lists depressive symptoms first. If the patient is known, or the primary problem area already identified, we recommend commencing the interview with the area of prominent symptomatology and concern to the patient, then completing all remaining sections.",
            None),
        "timeframe": bi(None, "Most recent 7 days.", "अंतिम 7 दिन।"),
        "ratingScale": {"min": 0, "max": 4, "note": bi(None,
            "Each item is rated 0 (absent) to 4 (severe) on the printed anchor set shown beside it; anchors are examples, not an exhaustive list, and when in doubt between two ratings the higher score is assigned.",
            "प्रत्येक आइटम छपाए हुए एंकर-समुच्चय के अनुसार 0 (अनुपस्थित) से 4 (गंभीर) तक रेट किया जाता है; एंकर उदाहरण हैं, पूर्ण सूची नहीं — दो रेटिंगों में संदेह हो तो उच्चतर अंक दें।")},
        "matrixOptions": [
            {"v": 0, "label": bi(None, "0 Absent", "0 अनुपस्थित")},
            {"v": 1, "label": bi(None, "1 Slight", "1 हल्का")},
            {"v": 2, "label": bi(None, "2 Mild", "2 मंद")},
            {"v": 3, "label": bi(None, "3 Moderate", "3 मध्यम")},
            {"v": 4, "label": bi(None, "4 Severe", "4 गंभीर")},
        ],
        "parts": parts,
        "sumScoring": True,
        "scoring": {
            "method": "biss_sectional_severity",
            "scaleMin": 0, "scaleMax": 4,
            "sections": {
                "depression": {"ids": DEP_IDS, "count": len(DEP_IDS), "maxTotal": len(DEP_IDS) * 4},
                "mania": {"ids": MAN_IDS, "count": len(MAN_IDS), "maxTotal": len(MAN_IDS) * 4},
            },
            "positiveItemValue": 2,
            "rule": bi(None,
                "Section totals are the sum of the item scores: Depression items 1-20 (0-80) and Mania items 21-44 (0-96). An item counts as symptomatic at score >= 2 (mild or worse). The published use of the BISS is dimensional - severity of bipolar signs and symptoms over 7 days and change over time - it has no diagnostic cutoff, so no total converts into a diagnosis. Item 4 (suicidality) >= 1 and items 25/39/43 >= 2 require immediate clinical review.",
                "विभाग-योग इतना है: अवसाद आइटम 1-20 (0-80) तथा उन्माद आइटम 21-44 (0-96)। स्कोर >= 2 पर आइटम लक्षणमान्य होता है। BISS का प्रकाशित प्रयोग विमात्मक (7 दिनों में द्विध्रुवी लक्षणों की तीव्रता एवं समय के साथ परिवर्तन) है — इसका कोई नैदानिक कटऑफ नहीं, अतः कुल अंक रोग-निर्णय नहीं बनाता। आइटम 4 >= 1 तथा 25/39/43 >= 2 पर तत्काल चिकित्सकीय समीक्षा आवश्यक।"),
            "disordersOnPositive": [],
            "interpretationNote": bi(None,
                "The BISS was designed to capture the full range of bipolar signs and symptoms rather than to generate a categorical diagnosis; interpret the depression and mania profiles together with the longitudinal course, collateral report and DSM-5/ICD criteria.",
                "BISS वर्गीकृत रोग-निर्णय हेतु नहीं, द्विध्रुवी लक्षणों की सम्पूर्ण श्रेणी पकड़ने हेतु निर्मित है; अवसाद एवं उन्माद प्रोफाइल को दीर्घानुक्रमिक पाठ्यक्रम, सह-सूचना एवं DSM-5/ICD मानदंडों संग पढ़ें।"),
        },
        "safetyItems": ["biss_4", "biss_25", "biss_39", "biss_43"],
        "sourcePages": "BISS (Bowden) version 1.5, 4/1/08, pages 1-7 of 7",
        "translationNote": bi(None,
            "Item text, probes and verbal anchors are the English original. Hindi is provided for the scale title only; the printed instrument is English-language and must be administered in English until a validated translation exists.",
            "आइटम-पाठ, प्रश्न एवं एंकर अंग्रेज़ी मूल से हैं। हिन्दी केवल शीर्षक हेतु; छपा मापनी अंग्रेज़ी में ही प्रयोज्य जब तक मान्यताप्त अनुवाद उपलब्ध न हो।"),
        "licensing": bi(None,
            "Copyright 2005 Charles L. Bowden, MD. Reproduction requires written permission; researchers and clinicians working in nonprofit or publicly owned settings (universities, nonprofit hospitals, government institutions) may make single copies of the BISS for their own use. Confirm the deployment setting qualifies before clinical or research use.",
            "प्रतिलिप्याधिकार 2005, चार्ल्स एल. बोडेन। पुनरुत्पादन हेतु लिखित अनुमति आवश्यक; गैर-लाभकारी/सार्वजनिक संस्थाओं के शोधकर्ता-चिकित्सक स्व-उपयोग हेतु एक प्रति बना सकते हैं। प्रयोग से पूर्व संस्था की पात्रता सुनिश्चित करें।"),
        "disorderKeys": BIPOLAR_DISORDERS,
    }


def domain_questions():
    """Screen-in items that deploy the BISS from the mood domain."""
    return [
        {
            "id": "mood_biss_1",
            "text": bi(None,
                "Has the person had a distinct period of abnormally elevated, expansive or irritable mood, or a clear history of hypomanic/manic episodes?",
                "क्या व्यक्ति का कोई सुस्पष्ट काल अत्युच्च/प्रसारित/कोपमय मूड का रहा है, या हाइपोमैनिक/मैनिक अवस्था का स्पष्ट इतिहास है?"),
            "sharedScale": "yesno",
            "scaleId": "biss",
            "disorders": ["bipolar_i_disorder", "bipolar_ii_disorder", "other_specified_bipolar"],
        },
        {
            "id": "mood_biss_2",
            "text": bi(None,
                "Is a 7-day severity profile of depressive AND manic symptoms needed to monitor the current episode or treatment response?",
                "क्या वर्तमान अवस्था या चिकित्सा-प्रतिक्रिया की निगरानी हेतु अवसादी एवं उन्मादी लक्षणों का 7-दिवसीय तीव्रता-प्रोफाइल आवश्यक है?"),
            "sharedScale": "yesno",
            "scaleId": "biss",
            "disorders": ["bipolar_depressive", "other_specified_bipolar"],
        },
    ]


def merge(data):
    changed = False
    data["scales"]["biss"] = build_scale()

    mood = next(d for d in data["domains"] if d["id"] == "mood")
    existing_ids = {q["id"] for q in mood["questions"]}
    for q in domain_questions():
        if q["id"] not in existing_ids:
            mood["questions"].append(q)
    # The mood domain keeps its PHQ-9 item scoring, so the BISS screen-ins must
    # not be summed with it: mark the domain as carrying an optional table route.
    if "auto:bipolartable" not in str(mood.get("instrument", "")):
        mood["optionalInstruments"] = (mood.get("optionalInstruments") or []) + \
            [x for x in ["auto:bipolartable"] if x not in (mood.get("optionalInstruments") or [])]

    data["instruments"]["BISS"] = {
        "name": "BISS (Bipolar Inventory of Signs and Symptoms Scale)",
        "construct": bi(None, "Bipolar signs and symptoms - dimensional severity over 7 days",
                        "द्विध्रुवी लक्षण — 7 दिनों की विमात्मक तीव्रता"),
        "format": bi(None, "44 items rated 0-4 by the clinician from self-report, family and interview observation; two sections (Depression 1-20, Mania 21-44)",
                     "44 आइटम, चिकित्सक द्वारा 0-4; दो विभाग (अवसाद 1-20, उन्माद 21-44)"),
        "duration": "~20 min interview",
        "language": {"en": "English", "hi": "अंग्रेज़ी (हिन्दी शीर्षक)"},
        "purpose": bi(None, "Quantify severity of bipolar signs and symptoms and track change; supports staging of an episode and treatment monitoring. Not diagnostic.",
                      "द्विध्रुवी लक्षणों की तीव्रता मापना एवं परिवर्तन-निगरानी; अवस्था-प्रबंधन व चिकित्सा-निगरानी में सहायक। रोग-निर्णायक नहीं।"),
        "source": "BISS, version 1.5 (4/1/08), Charles L. Bowden et al.",
        "licensing": bi(None,
            "Copyright 2005 Charles L. Bowden, MD. Single copies permitted for researchers/clinicians in nonprofit or publicly owned settings; otherwise written permission required.",
            "प्रतिलिप्याधिकार 2005 चार्ल्स एल. बोडेन; गैर-लाभकारी/सार्वजनिक संस्थाओं हेतु एक-प्रति छूट, अन्यथा लिखित अनुमति आवश्यक।"),
    }

    note = ("BISS implemented as scales.biss (Bipolar Inventory of Signs and Symptoms Scale, "
            "Bowden v1.5 4/1/08): 44 clinician-rated items scored 0-4 over the most recent 7 days, "
            "each with its own printed verbal anchors, item definition and probe questions. "
            "Depression section items 1-20 (0-80), Mania section items 21-44 (0-96); an item counts "
            "as symptomatic at >= 2. Dimensional severity measure with no diagnostic cutoff - the "
            "score never produces a bipolar diagnosis, it describes severity and change. Reached "
            "through the mood domain via routing auto:bipolartable. Items 4 (suicidality), 25 "
            "(aggression), 39 (risky behaviour) and 43 (hallucinations) are safety-flagged.")
    notes = data["meta"].setdefault("instrumentNotes", [])
    if note not in notes:
        notes.append(note)

    ver = data["meta"].get("schemaVersion", "")
    if ver == "2.7.0":
        data["meta"]["schemaVersion"] = "2.8.0"
    return data


def main():
    check = "--check" in sys.argv
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    before = json.dumps(data, sort_keys=True, ensure_ascii=False)
    data = merge(data)
    after = json.dumps(data, sort_keys=True, ensure_ascii=False)

    assert len(data["scales"]["biss"]["parts"][0]["questions"]) == 20
    assert len(data["scales"]["biss"]["parts"][1]["questions"]) == 24
    for p in data["scales"]["biss"]["parts"]:
        for q in p["questions"]:
            assert len(q["anchors"]) == 5, q["id"]
            assert q["probes"], q["id"]
    for k in BIPOLAR_DISORDERS:
        assert k in data["disorders"], k

    if check:
        print("would write schema %s | BISS items: %d | changed: %s"
              % (data["meta"]["schemaVersion"], 44, before != after))
        return 0
    if before == after:
        print("data.json already up to date (schema %s)" % data["meta"]["schemaVersion"])
        return 0
    with open(DATA, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print("wrote data.json schema %s | BISS items: 44 (D 20 / M 24)"
          % data["meta"]["schemaVersion"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
