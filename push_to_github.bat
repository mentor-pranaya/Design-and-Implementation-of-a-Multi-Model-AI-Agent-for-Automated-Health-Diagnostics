@echo off
echo ========================================
echo Pushing Documentation Updates to GitHub
echo ========================================
echo.

echo Checking Git status...
git status
echo.

echo Staging modified documentation files...
git add -u
echo.

echo Committing changes...
git commit -m "docs: formalize documentation and remove emojis for professional presentation - Removed all emojis from documentation files - Replaced emojis with professional text equivalents - Formalized language throughout documentation - Changed informal language to formal third-person perspective - Updated casual phrases to professional terminology"
echo.

echo Pushing to GitHub branch Nima_Fathima...
git push origin Nima_Fathima
echo.

echo ========================================
echo Done! Check the output above for any errors.
echo ========================================
pause
