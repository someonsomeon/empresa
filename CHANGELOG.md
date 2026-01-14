# Changelog

## 2026-01-13
- Replaced custom UI with minimal native Tkinter UI for `LoginWindow` and `RecoveryWindow`.
- Replaced neumorphic `NeuButton` with a simplified flat rounded button (square-ish with rounded corners and font-size ~18px), removed complex shadows. Application background remains white.
- Replaced 'Recuperar contraseña' button with a 'Regístrate' button and added a clickable blue label that opens the recovery dialog prefilled with the Usuario field content. Added a basic registration flow (username, email, password).
- Centered login buttons and recovery label; recovery dialog now uses larger fonts, has the send button centered and cannot be resized.
- Login: on incorrect username/password the entry borders turn red and the window vibrates (shake) to indicate error; borders reset automatically.
- Added `RegisterWindow` with fields Usuario/Correo/Contraseña and a centered "Aceptar" button using `NeuButton`. Labels for Usuario/Contraseña on login are now centered above their fields.
- Email recovery: the input shows a local-part textbox with a gray square (domain pill) above-right displaying `@gmail.com` and placeholder behavior for the local part.
- Added a centered "Cerrar sesión" button to the main panel; on logout the main window closes and a fresh empty login window is shown (login fields cleared).
- Preserved existing authentication and recovery logic.
- Ensured `send_code` runs in a background thread and added `SMTP_TIMEOUT` to avoid UI freezes.
- Small robustness fixes: initialized `send_btn`, `status`, and `resend_btn` in `RecoveryWindow`.
