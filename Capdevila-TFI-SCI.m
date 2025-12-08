%% =========================================================================
%  TFI - Sistemas de Control
%  Autor: Gastón Capdevila
%  Año: 2025
%
% Este script implementa el flujo principal para el Trabajo Final
% =========================================================================

pkg load control
pkg load symbolic
clear all;
close all;
clc;

s=tf('s')

%% ========================================================================
%       PARÁMETROS DEL SISTEMA
% ========================================================================

K_sensor = 0.03;          % Ganancia del sensor
T_sensor = 5;             % Constante de tiempo del sensor[s]

K_cava = 30;              % Ganancia de la cava
T_cava = 45;              % Constante de tiempo de la cava[s]

K_hum = 0.66;             % Ganancia del humidificador
T_hum = 5;                % Constante de tiempo del humidificador[s]

K = 5/3;                  % GANANCIA K

%% ========================================================================
%                           FdTLA
% ========================================================================

FT_sensor = tf([K_sensor],[T_sensor 1]);
FT_cava = tf([K_cava],[T_cava 1]);
FT_hum = tf([K_hum],[T_hum 1]);

G = FT_cava*FT_hum;
H = FT_sensor*K;

FdTLA = G*H

FdTLA_min_real = minreal(FdTLA)

% ========================================================================
%                   Calcular ceros, polos y ganancia
% ========================================================================

pole(FdTLA)

z = zero(FdTLA)
p = pole(FdTLA)
k = dcgain(FdTLA)

% ========================================================================
%                          RESPUESTA TEMPORAL
% ========================================================================

t = 0:1:500;
[y, t] = step(3.5*FdTLA, t);

figure;
plot(t, y, 'LineWidth', 2);
grid on;
xlabel('Tiempo [s]');
ylabel('Salida');
title('Respuesta al escalón - Lazo abierto');

final_value = y(end);
idx = find(abs(y - final_value) <= 0.06 * abs(final_value), 1);
Ts = t(idx);

y5 = 0.05 * final_value;
y95 = 0.95 * final_value;

t5 = t(find(y >= y5, 1));
t95 = t(find(y >= y95, 1));
Tr = t95 - t5;

max_value = max(y);
OS = (max_value - final_value) / final_value * 100;

tau_est = t(find(y >= 0.6 * final_value, 1));

K_estatica = dcgain(FdTLA);

printf("\n========================================\n");
printf("  ANALISIS DE RESPUESTA TEMPORAL\n");
printf("========================================\n");
printf("  Valor final                  : %.4f\n", final_value);
printf("  Tiempo de establecimiento    : %.2f s\n", Ts);
printf("  Tiempo de subida             : %.2f s\n", Tr);
printf("  Sobrepaso SO                 : %.2f %%\n", OS);
printf("  K estatica                   : %.2f \n", K_estatica);
printf("========================================\n\n");

% ========================================================================
%                          ERROR EN ESTADO ESTABLE
% ========================================================================

Kp = dcgain(FdTLA);
ess = 1 / (1 + Kp);
fprintf("Ganancia DC (Kp)                 : %.4f\n", Kp);
fprintf("Error en estado estable          : %.4f\n\n", ess);

%% ========================================================================
%                               COMPENSACION
% ========================================================================

%% ============== FUNCION PARA EVALUAR FdT ==========================
function val = tf_eval(G, s0)
    [num, den] = tfdata(G, "vector");
    Ns = polyval(num, s0);
    Ds = polyval(den, s0);
    val = Ns / Ds;
end

Pi = (s + 0.0222)/s
rlocus(Pi*FdTLA)
s0 = -0.0665;

invK = tf_eval(Pi*FdTLA, s0)

Kp = 1 / abs(invK)

PI = Kp*Pi

FdTLA_Compensada = PI*G*H

Gcomp = G*PI

FdTLC_Compensada = feedback(Gcomp, H)

pole(FdTLC_Compensada)
pzmap(FdTLC_Compensada)

% ========================================================================
%                 RESPUESTA TEMPORAL SISTEMA COMPENSADO
% ========================================================================

t = 0:1:250;
[y, t] = step(3.5*FdTLC_Compensada, t);

final_value = y(end);
idx = find(abs(y - final_value) <= 0.053 * abs(final_value), 1);
Ts = t(idx);

y5 = 0.05 * final_value;
y95 = 0.95 * final_value;

t5 = t(find(y >= y5, 1));
t95 = t(find(y >= y95, 1));
Tr = t95 - t5;

max_value = max(y);
OS = (max_value - final_value) / final_value * 100;

printf("\n=============================================\n");
printf(" RESPUESTA TEMPORAL LAZO CERRADO COMPENSADO\n");
printf("=============================================\n");
printf("  Valor final                  : %.4f\n", final_value);
printf("  Tiempo de establecimiento    : %.2f s\n", Ts);
printf("  Tiempo de subida             : %.2f s\n", Tr);
printf("  Sobrepaso SO                 : %.2f %%\n", OS);
printf("========================================\n\n");

figure;
plot(t, y, 'LineWidth', 1.5);
hold on;
plot([t(1) t(end)], [final_value final_value], 'r--', 'LineWidth', 1.2);
legend('Salida', 'Valor final');
title('Respuesta al escalón - Lazo cerrado compensado');
xlabel('Tiempo [s]');
ylabel('Salida [%HR]');
grid on;
hold off;

% Ganancia DC del lazo cerrado (referencia [V] -> %RH)
Kcl_hum = dcgain(FdTLC_Compensada)   % [ %RH / V ]

% Si queremos ver qué %RH da un escalón 0->5V:
V_aplic = 5;
RH_from_5V = Kcl_hum * V_aplic

% Para alcanzar 70 %RH
Y_target = 70;   % %RH objetivo
V_req = Y_target / Kcl_hum   % [V]

% Estabilidad relativa
margin(FdTLA_Compensada)

% ========================================================================
%               ERROR EN ESTADO ESTABLE SISTEMA COMPENSADO
% ========================================================================

fprintf("\nError en estado estable del sistema compensado\n", ess);
K_ess_comp = dcgain(FdTLA_Compensada)
ess_comp = 1 / (1 + K_ess_comp);
fprintf("Error en estado estable: %.4f\n\n", ess_comp);