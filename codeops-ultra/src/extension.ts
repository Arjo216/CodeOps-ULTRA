// codeops-ultra/src/extension.ts
import * as vscode from 'vscode';
import axios from 'axios';

export function activate(context: vscode.ExtensionContext) {
    console.log('CodeOps ULTRA Enterprise Extension is now active!');

    // Create a dedicated output channel for our Docker logs
    const outputChannel = vscode.window.createOutputChannel('CodeOps ULTRA Sandbox');

    let disposable = vscode.commands.registerCommand('codeops-ultra.audit', async () => {
        
        // 1. Get the active text editor
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('CodeOps ULTRA: No active file open to audit.');
            return;
        }

        // 2. Grab the code and the language natively from VS Code!
        const document = editor.document;
        const codeContent = document.getText();
        const languageId = document.languageId; 

        if (!codeContent.trim()) {
            vscode.window.showWarningMessage('CodeOps ULTRA: The file is empty.');
            return;
        }

        // 3. Show a loading notification for Static Analysis
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `ULTRA: Auditing ${languageId.toUpperCase()} Code...`,
            cancellable: false
        }, async (progress) => {
            try {
                // 4. Send to our Python FastAPI Backend (Fast Gear)
                const response = await axios.post('http://127.0.0.1:8000/api/v2/agent/review', {
                    code: codeContent,
                    language: languageId
                });

                if (response.data.error) {
                    vscode.window.showErrorMessage(`ULTRA Error: ${response.data.error}`);
                    return;
                }

                const aiOptimizedCode = response.data.ai_analysis;

                // 5. Open a new split-screen document to show the verified code!
                const newDoc = await vscode.workspace.openTextDocument({
                    content: aiOptimizedCode,
                    language: languageId
                });
                
                await vscode.window.showTextDocument(newDoc, vscode.ViewColumn.Beside);
                
                // 6. THE OPTIONAL SANDBOX PROMPT
                const userChoice = await vscode.window.showInformationMessage(
                    `CodeOps ULTRA: Audit Complete. Verified Safe. Do you want to execute this in the Secure Docker Sandbox?`,
                    '🚀 Deploy to Sandbox',
                    'Dismiss'
                );

                // 7. THE HEAVY GEAR EXECUTION
                if (userChoice === '🚀 Deploy to Sandbox') {
                    
                    // Show the output panel and clear previous logs
                    outputChannel.show(true);
                    outputChannel.clear();
                    outputChannel.appendLine(`[ULTRA] Initializing Ephemeral ${languageId.toUpperCase()} Container...`);

                    vscode.window.withProgress({
                        location: vscode.ProgressLocation.Notification,
                        title: `ULTRA: Executing inside Docker Sandbox...`,
                        cancellable: false
                    }, async () => {
                        try {
                            const sandboxRes = await axios.post('http://127.0.0.1:8000/api/solve', {
                                task: `Execute this exact code:\n\n${aiOptimizedCode}`,
                                language: languageId
                            });

                            const logs = sandboxRes.data.logs || [];
                            outputChannel.appendLine(`[ULTRA] --- LIVE CONTAINER LOGS ---\n`);
                            
                            logs.forEach((log: string) => {
                                outputChannel.appendLine(log);
                            });

                            outputChannel.appendLine(`\n[ULTRA] ✅ Execution Finished. Sandbox Wiped.`);
                            vscode.window.showInformationMessage('CodeOps ULTRA: Sandbox Execution Complete.');

                        } catch (err: any) {
                            outputChannel.appendLine(`[ULTRA ERROR] Execution Engine Failure: ${err.message}`);
                            vscode.window.showErrorMessage('CodeOps ULTRA: Sandbox Execution Failed.');
                        }
                    });
                }

            } catch (error: any) {
                vscode.window.showErrorMessage(`ULTRA Connection Failure: Ensure your backend (localhost:8000) is running. ${error.message}`);
            }
        });
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}