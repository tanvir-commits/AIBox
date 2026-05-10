from app.services.rag import _overlap_score


def test_overlap_timer_question_matches_tim_tokens_not_word_timer() -> None:
    q = "how many timer stm32 has"
    chunk = "The STM32F405xx includes TIM1, TIM2, TIM3, TIM4, TIM5, and TIM8 timers."
    assert _overlap_score(q, chunk) >= 2


def test_overlap_adc_question_matches_adc12_style() -> None:
    q = "how many adcs"
    chunk = "The device integrates three ADC12 modules (ADC1, ADC2, ADC3) with 12-bit resolution."
    assert _overlap_score(q, chunk) >= 2
