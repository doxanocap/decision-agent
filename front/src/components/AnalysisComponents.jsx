import { AlertCircle, AlertTriangle, CheckCircle, HelpCircle, Info } from 'lucide-react';
import { useState } from 'react';

/**
 * Confidence Level Badge with Explanation
 * Shows why the analysis has a certain confidence level
 */
export const ConfidenceBadge = ({ level, scoreDetails }) => {
    const [showExplanation, setShowExplanation] = useState(false);

    const config = {
        high: {
            color: 'bg-green-500/20 text-green-400 border-green-500/30',
            icon: CheckCircle,
            label: 'Высокая уверенность',
            explanation: 'Аргументы детальные, логически связаны и подкреплены фактами. Анализ надежен.'
        },
        medium: {
            color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
            icon: AlertTriangle,
            label: 'Средняя уверенность',
            explanation: 'Аргументы в целом логичны, но есть слабые места. Рекомендуем добавить больше деталей.'
        },
        low: {
            color: 'bg-red-500/20 text-red-400 border-red-500/30',
            icon: AlertCircle,
            label: 'Низкая уверенность',
            explanation: 'Аргументы слишком короткие или противоречат прошлым решениям. Добавьте больше обоснований.'
        }
    };

    const { color, icon: Icon, label, explanation } = config[level] || config.medium;

    return (
        <div className="relative">
            <div
                className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${color} cursor-help`}
                onMouseEnter={() => setShowExplanation(true)}
                onMouseLeave={() => setShowExplanation(false)}
            >
                <Icon size={16} />
                <span className="text-sm font-semibold">{label}</span>
                <HelpCircle size={14} className="opacity-50" />
            </div>

            {showExplanation && (
                <div className="absolute top-full left-0 mt-2 w-80 bg-zinc-900 border border-zinc-700 rounded-lg p-4 shadow-xl z-50">
                    <p className="text-sm text-zinc-300 mb-3">{explanation}</p>

                    {scoreDetails && (
                        <div className="space-y-2">
                            <div className="text-xs text-zinc-500 font-semibold mb-2">Детали оценки:</div>

                            <div className="space-y-1.5">
                                <ScoreBar
                                    label="Логическая связность"
                                    value={scoreDetails.logic_stability}
                                    tooltip="Насколько хорошо аргументы связаны между собой"
                                />
                                <ScoreBar
                                    label="Опора на факты"
                                    value={scoreDetails.data_grounding}
                                    tooltip="Факты vs эмоции"
                                />
                                <ScoreBar
                                    label="Согласованность с прошлым"
                                    value={scoreDetails.historical_consistency}
                                    tooltip="Соответствие вашим предыдущим решениям"
                                />
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

/**
 * Score Bar for detailed metrics
 */
const ScoreBar = ({ label, value, tooltip }) => {
    const percentage = Math.round(value * 100);
    const color = value >= 0.7 ? 'bg-green-500' : value >= 0.4 ? 'bg-yellow-500' : 'bg-red-500';

    return (
        <div className="group relative">
            <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-400">{label}</span>
                <span className="text-zinc-300 font-semibold">{percentage}%</span>
            </div>
            <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                <div
                    className={`h-full ${color} transition-all duration-500`}
                    style={{ width: `${percentage}%` }}
                />
            </div>

            {/* Tooltip */}
            <div className="absolute bottom-full left-0 mb-2 w-48 bg-zinc-950 border border-zinc-700 rounded px-2 py-1 text-xs text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                {tooltip}
            </div>
        </div>
    );
};

/**
 * ML Score Explanation
 * Explains what 8/100 or 75/100 means
 */
export const ScoreExplanation = ({ score, argumentText }) => {
    const [showDetails, setShowDetails] = useState(false);

    const getScoreCategory = (score) => {
        if (score >= 70) return {
            label: 'Сильный аргумент',
            color: 'text-green-400',
            icon: CheckCircle,
            explanation: 'Этот аргумент хорошо обоснован, логичен и содержит достаточно деталей.'
        };
        if (score >= 40) return {
            label: 'Средний аргумент',
            color: 'text-yellow-400',
            icon: AlertTriangle,
            explanation: 'Аргумент логичен, но можно добавить больше фактов или примеров для убедительности.'
        };
        return {
            label: 'Слабый аргумент',
            color: 'text-red-400',
            icon: AlertCircle,
            explanation: 'Аргумент слишком короткий или не содержит четкого обоснования. Добавьте "потому что..." и конкретные причины.'
        };
    };

    const { label, color, icon: Icon, explanation } = getScoreCategory(score);

    return (
        <div className="relative">
            <div
                className="inline-flex items-center gap-2 cursor-help"
                onMouseEnter={() => setShowDetails(true)}
                onMouseLeave={() => setShowDetails(false)}
            >
                <span className={`text-2xl font-bold ${color}`}>{Math.round(score)}</span>
                <span className="text-zinc-500 text-sm">/100</span>
                <HelpCircle size={16} className="text-zinc-600" />
            </div>

            {showDetails && (
                <div className="absolute top-full left-0 mt-2 w-96 bg-zinc-900 border border-zinc-700 rounded-lg p-4 shadow-xl z-50">
                    <div className="flex items-center gap-2 mb-3">
                        <Icon size={18} className={color} />
                        <span className={`font-semibold ${color}`}>{label}</span>
                    </div>

                    <p className="text-sm text-zinc-300 mb-3">{explanation}</p>

                    {score < 40 && (
                        <div className="bg-zinc-800/50 border border-zinc-700 rounded p-3">
                            <div className="text-xs font-semibold text-zinc-400 mb-2">💡 Как улучшить:</div>
                            <ul className="text-xs text-zinc-400 space-y-1">
                                <li>• Добавьте конкретные причины ("потому что...", "так как...")</li>
                                <li>• Приведите факты или примеры</li>
                                <li>• Увеличьте длину до минимум 50 символов</li>
                                <li>• Объясните логическую связь между причиной и выводом</li>
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

/**
 * Error Display Component
 * Beautiful error states with retry functionality
 */
export const ErrorDisplay = ({ error, onRetry }) => {
    const getErrorConfig = (errorType) => {
        switch (errorType) {
            case 'INSUFFICIENT_DATA':
                return {
                    icon: Info,
                    color: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
                    title: 'Недостаточно данных для анализа',
                    message: 'Некоторые аргументы слишком короткие или не содержат обоснования.',
                    action: 'Добавьте больше деталей',
                    showRetry: false
                };
            case 'LLM_ANALYSIS_FAILED':
                return {
                    icon: AlertCircle,
                    color: 'bg-red-500/10 border-red-500/20 text-red-400',
                    title: 'ИИ временно недоступен',
                    message: error.user_message || 'Попробуйте еще раз через минуту.',
                    action: 'Повторить попытку',
                    showRetry: true
                };
            case 'ML_SCORING_FAILED':
                return {
                    icon: AlertCircle,
                    color: 'bg-red-500/10 border-red-500/20 text-red-400',
                    title: 'Ошибка оценки аргументов',
                    message: error.user_message || 'Не удалось оценить качество аргументов.',
                    action: 'Попробовать снова',
                    showRetry: true
                };
            default:
                return {
                    icon: AlertTriangle,
                    color: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
                    title: 'Что-то пошло не так',
                    message: error.user_message || 'Произошла ошибка. Попробуйте позже.',
                    action: 'Повторить',
                    showRetry: true
                };
        }
    };

    const config = getErrorConfig(error.error);
    const Icon = config.icon;

    return (
        <div className={`border rounded-lg p-6 ${config.color}`}>
            <div className="flex items-start gap-4">
                <div className="p-3 rounded-full bg-current/10">
                    <Icon size={24} className="text-current" />
                </div>

                <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-2">{config.title}</h3>
                    <p className="text-sm opacity-90 mb-4">{config.message}</p>

                    {error.invalid_arguments && error.invalid_arguments.length > 0 && (
                        <div className="bg-zinc-900/50 rounded p-3 mb-4">
                            <div className="text-xs font-semibold mb-2">Проблемные аргументы:</div>
                            <ul className="space-y-2">
                                {error.invalid_arguments.map((arg, i) => (
                                    <li key={i} className="text-xs">
                                        <span className="text-zinc-400">{arg.variant}:</span>{' '}
                                        <span className="text-zinc-300 italic">"{arg.text}"</span>
                                        <div className="text-red-400 mt-1">→ {arg.reason}</div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {config.showRetry && onRetry && (
                        <button
                            onClick={onRetry}
                            className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-semibold transition-colors"
                        >
                            {config.action}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

/**
 * Systemic Inconsistency Warning
 * Shows contradictions with past decisions
 */
export const InconsistencyWarning = ({ inconsistencies }) => {
    if (!inconsistencies || inconsistencies.length === 0) return null;

    return (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-5">
            <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-full bg-yellow-500/20">
                    <AlertTriangle size={20} className="text-yellow-400" />
                </div>
                <h4 className="text-yellow-400 font-semibold text-lg">
                    Обнаружены противоречия с прошлыми решениями
                </h4>
            </div>

            <div className="space-y-4">
                {inconsistencies.map((conflict, i) => (
                    <div key={i} className="bg-zinc-900/50 rounded-lg p-4 space-y-3">
                        <div>
                            <div className="text-xs text-zinc-500 font-semibold mb-1">Раньше вы считали:</div>
                            <p className="text-sm text-zinc-300 italic bg-zinc-800/50 rounded p-2">
                                "{conflict.past_statement}"
                            </p>
                        </div>

                        <div>
                            <div className="text-xs text-zinc-500 font-semibold mb-1">Сейчас вы утверждаете:</div>
                            <p className="text-sm text-zinc-300 italic bg-zinc-800/50 rounded p-2">
                                "{conflict.current_statement}"
                            </p>
                        </div>

                        <div className="pt-2 border-t border-zinc-700">
                            <p className="text-sm text-yellow-300">{conflict.conflict_description}</p>
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-4 bg-zinc-900/50 rounded p-3">
                <p className="text-xs text-zinc-400">
                    💡 <strong>Это не ошибка</strong> — ваши ценности могут меняться со временем.
                    Но важно осознавать эти изменения и понимать, почему они произошли.
                </p>
            </div>
        </div>
    );
};
